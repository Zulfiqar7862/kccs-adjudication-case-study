"""Real HTTP walkthrough using wholly fictional data and explicit source stubs."""
import json
import secrets
import tempfile
import threading
from pathlib import Path
from http.client import HTTPConnection

from sentinel.api.http import make_server
from sentinel.fixtures.sample import create_workbook
from sentinel.workflow.service import Engine, verify_export


def run_demo(narrate=None):
    say = narrate or (lambda message: None)
    with tempfile.TemporaryDirectory(prefix='sentinel-demo-') as directory:
        root = Path(directory)
        source = create_workbook(root / 'sample.xlsx')
        engine = Engine(root / 'demo.db')
        imported = engine.ingest(source)
        say(f"Step 1  Import: fictional workbook -> {imported['created']} cases, all WAITING_EVIDENCE "
            f"(source SHA-256 {imported['import_hash'][:12]}...)")
        constraints = engine.tables()['12_Tenant_Constraints']
        tenant = next(row['tenant_code'] for row in constraints if '(dual)' in row['who_signs_a_disposition'])
        credentials, tokens = {}, {}
        for role in ['reviewer', 'site_qa', 'corporate_qa', 'regulatory']:
            token = secrets.token_urlsafe(32)
            tokens[role] = token
            credentials[token] = {'tenant': tenant, 'actor': f'demo-{role}', 'role': role}
        server = make_server(engine, credentials)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        steps, sequence = [], 0
        try:
            def request(method, path, role='reviewer', body=None):
                nonlocal sequence
                sequence += 1
                connection = HTTPConnection('127.0.0.1', server.server_port, timeout=10)
                try:
                    connection.request(method, path,
                                       body=json.dumps(body).encode() if body is not None else None,
                                       headers={'Authorization': f'Bearer {tokens[role]}',
                                                'Content-Type': 'application/json',
                                                'Idempotency-Key': f'demo-{sequence}'})
                    response = connection.getresponse()
                    return response.status, json.loads(response.read())
                finally:
                    connection.close()


            status, health = request('GET', '/health')
            if status != 200 or health['status'] != 'ok':
                raise AssertionError('Health check failed')
            _, cases = request('GET', '/cases')
            case_id = cases[0]['id']
            base = f'/cases/{case_id}'
            _, case = request('GET', base)
            version = case['version']
            say(f'Step 2  API: GET /health ok; tenant {tenant} (dual sign-off) sees {len(cases)} cases; '
                f"working on {case_id}, state {case['state']}, {len(case['packet']['analysis']['blockers'])} blockers")

            def command(action, body, role='reviewer', expected_status=200):
                nonlocal version
                status, result = request('POST', base + '/' + action, role, dict(body, expected_version=version))
                if status != expected_status:
                    raise AssertionError((action, status, result))
                if status == 200:
                    version = result['version']
                steps.append({'action': action, 'http_status': status, 'state': result.get('state')})
                return result

            command('sign', {'disposition': 'RELEASE_WITH_NOTE', 'rationale': 'Blocked without evidence'}, 'site_qa', 409)
            say('Step 3  Guard: signing before evidence review is rejected with HTTP 409')
            refs = []
            for kind in ['SOP', 'STABILITY', 'TELEMETRY', 'IDENTITY', 'BATCH', 'CONTRACT']:
                command('evidence', {'kind': kind, 'source_ref': f'demo-stub://{kind}',
                                    'content': f'FICTIONAL TEST STUB: {kind}. Not authoritative evidence.'})
                refs.append(f'E{len(refs) + 1}')
            command('review', {'resolutions': {blocker: refs for blocker in case['packet']['analysis']['blockers']},
                               'note': 'Fictional walkthrough: structural workflow only.'})
            say('Step 4  Evidence: reviewer attaches SOP, STABILITY, TELEMETRY, IDENTITY, BATCH, CONTRACT (E1-E6), '
                'resolves every blocker -> READY_FOR_REVIEW')
            first = command('sign', {'disposition': 'RELEASE_WITH_NOTE', 'rationale': 'Fictional site approval'}, 'site_qa')
            if first['state'] != 'READY_FOR_REVIEW':
                raise AssertionError('Dual signature gate failed')
            say('Step 5  Sign: site QA signs; case stays READY_FOR_REVIEW because the tenant needs two signatures')
            final = command('sign', {'disposition': 'RELEASE_WITH_NOTE', 'rationale': 'Fictional corporate approval'}, 'corporate_qa')
            if final['state'] != 'DISPOSED':
                raise AssertionError('Disposition failed')
            say('Step 6  Sign: corporate QA signs the same disposition -> DISPOSED (RELEASE_WITH_NOTE)')
            _, before = request('GET', base + '/audit')
            if not verify_export(before):
                raise AssertionError('Audit verification failed')
            say(f"Step 7  Audit: {len(before['audit'])} hash-chained audit entries exported and verified")
            command('reopen', {'reason': 'Fictional late evidence requires fresh review'})
            _, after = request('GET', base + '/audit')
            if not verify_export(after) or before['revisions'][0] != after['revisions'][0] or len(after['revisions']) != 2:
                raise AssertionError('Historical revision preservation failed')
            say('Step 8  Reopen: late evidence opens revision 2; signed revision 1 is unchanged and still verifies')

            def unavailable(key, payload):
                raise ConnectionError('Fictional outage')
            failed = engine.tick(tenant, unavailable)
            delivered = engine.tick(tenant, lambda key, payload: None)
            if not failed or any(row['delivered'] for row in failed) or not all(row['delivered'] for row in delivered):
                raise AssertionError('Reminder retry failed')
            if any(row['receipt'] for row in engine.notifications(tenant)):
                raise AssertionError('Internal reminder fabricated a regulatory receipt')
            say(f'Step 9  Clock: reminder delivery fails during an outage ({len(failed)} pending), succeeds on retry; '
                'no regulator receipt is invented')
            return {'result': 'PASS', 'source': 'generated fictional workbook', 'imported_cases': imported['created'],
                    'http_lifecycle': steps, 'audit_integrity': 'PASS', 'prior_revision_preserved': True,
                    'reminder_failure_and_retry': 'PASS', 'regulators_not_notified': True}
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
