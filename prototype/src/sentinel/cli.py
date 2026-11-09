"""Command-line entry point for local development and authorized workbook replay."""
import argparse
import json
import os
import secrets
import sqlite3
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree.ElementTree import ParseError

from defusedxml.common import DefusedXmlException

from sentinel.config import output_directory
from sentinel.workflow.service import DomainError, Engine, verify_export


def output(value, path=None):
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        # Confirm the write without echoing private file contents to the terminal.
        print(json.dumps({'written': target.as_posix()}, indent=2) + '\n', end='')
    else:
        print(text, end='')


def imported_tenants(engine):
    return sorted({event['tenant_code'] for event in engine.tables()['01_Excursion_Events']})


def main():
    parser = argparse.ArgumentParser(description='Local evidence-first adjudication workflow')
    try:
        directory = output_directory()
    except ValueError as exc:
        parser.error(str(exc))
    parser.add_argument('--db', default=str(directory / 'sentinel.db'), help='Local SQLite path (default: prototype/output/sentinel.db)')
    commands = parser.add_subparsers(dest='command', required=True)
    sample = commands.add_parser('sample', help='Generate a wholly fictional workbook')
    sample.add_argument('--output', default=str(directory / 'sample.xlsx'))
    demo = commands.add_parser('demo', help='Exercise the full HTTP lifecycle on fictional data in a temporary database')
    demo.add_argument('--explain', action='store_true', help='Print a plain-English line for each step before the JSON result')
    imp = commands.add_parser('import', help='Import one authorized workbook snapshot atomically')
    imp.add_argument('workbook')
    report = commands.add_parser('report', help='Summarize imported evidence blockers and notification clocks')
    report.add_argument('--output', help='Full report includes source-derived private data; keep it local')
    serve = commands.add_parser('serve', help='Start the authenticated loopback JSON API')
    serve.add_argument('--credentials', default=str(directory / 'local-credentials.json'))
    serve.add_argument('--port', type=int, default=8080)
    credentials = commands.add_parser('credentials', help='Generate private local-only bearer identities')
    credentials.add_argument('--tenant', action='append', required=True)
    credentials.add_argument('--output', default=str(directory / 'local-credentials.json'))
    export = commands.add_parser('export', help='Export a private tenant case audit bundle')
    export.add_argument('--tenant', required=True)
    export.add_argument('--case', required=True)
    export.add_argument('--output', required=True)
    verify = commands.add_parser('verify', help='Verify an exported audit bundle')
    verify.add_argument('file')
    tick = commands.add_parser('tick', help='Run internal reminder stub; never files with a regulator')
    tick.add_argument('--tenant', required=True)
    tick.add_argument('--fail', action='store_true')
    assess = commands.add_parser('assess', help='Assess one imported alert as a tenant principal; writes an evidence package')
    assess.add_argument('--tenant', required=True, help='Principal tenant; events of other tenants are not visible')
    assess.add_argument('--event', required=True)
    assess.add_argument('--known-at', help='Knowledge cutoff (ISO 8601); facts recorded later are hidden')
    assess.add_argument('--corrections', help='JSON list of correction overlays with recorded_at')
    assess.add_argument('--output', help='Evidence package path; stdout when omitted')
    assess_all = commands.add_parser('assess-all', help='Assess every imported alert and summarize coverage, conflicts and abstentions')
    assess_all.add_argument('--known-at')
    assess_all.add_argument('--output', required=True, help='Summary JSON path; contains aggregates and event ids only')
    assess_all.add_argument('--compare-history', action='store_true',
                            help='Evaluation layer: list review candidates where the historical disposition conflicts with assessment findings')
    verify_assessment = commands.add_parser('verify-assessment', help='Verify an evidence package written by assess')
    verify_assessment.add_argument('file')
    args = parser.parse_args()
    try:
        if args.command == 'sample':
            from sentinel.fixtures.sample import create_workbook
            create_workbook(args.output)
            output({'source': 'fictional', 'workbook': args.output})
            return
        if args.command == 'demo':
            from .demo import run_demo
            output(run_demo(print if args.explain else None))
            return
        if args.command == 'credentials':
            identities = {}
            for tenant in sorted(set(args.tenant)):
                if not tenant.strip():
                    raise ValueError('Tenant must not be blank')
                for role in ['reviewer', 'signer', 'site_qa', 'corporate_qa', 'regulatory']:
                    identities[secrets.token_urlsafe(32)] = {'tenant': tenant, 'actor': f'local-{tenant}-{role}', 'role': role}
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                raise ValueError(f'{path} already exists; pass --output with a new path or remove the old file') from None
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                json.dump(identities, stream, indent=2)
            output({'created': str(path), 'identities': len(identities), 'notice': 'Local only. Keep this file private.'})
            return
        if args.command == 'verify':
            try:
                valid = verify_export(json.loads(Path(args.file).read_text(encoding='utf-8')))
            except (KeyError, TypeError, ValueError):
                valid = False
            output({'valid': valid})
            raise SystemExit(0 if valid else 1)
        if args.command == 'verify-assessment':
            from sentinel.evidence.assessment import verify_package
            try:
                valid = verify_package(json.loads(Path(args.file).read_text(encoding='utf-8')))
            except (KeyError, TypeError, ValueError):
                valid = False
            output({'valid': valid})
            raise SystemExit(0 if valid else 1)
        path = Path(args.db)
        path.parent.mkdir(parents=True, exist_ok=True)
        engine = Engine(path)
        if args.command == 'import':
            output(engine.ingest(args.workbook))
        elif args.command == 'serve':
            from sentinel.api.http import make_server
            credentials_path = Path(args.credentials)
            if not credentials_path.is_file():
                raise ValueError(f'{credentials_path} not found; run `python -m sentinel credentials --tenant <CODE>` first')
            identities = json.loads(credentials_path.read_text(encoding='utf-8'))
            server = make_server(engine, identities, port=args.port)
            print(f'Local API http://127.0.0.1:{server.server_port} (Ctrl-C to stop)', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        elif args.command == 'export':
            output(engine.export(args.tenant, args.case), args.output)
        elif args.command == 'assess':
            from sentinel.evidence.assessment import AccessDenied, assess, package
            corrections = json.loads(Path(args.corrections).read_text(encoding='utf-8')) if args.corrections else None
            try:
                result = assess(engine.tables(), args.event, principal_tenant=args.tenant, known_at=args.known_at, corrections=corrections)
            except AccessDenied as denied:
                raise DomainError(str(denied), 404) from None
            output(package(result), args.output)
        elif args.command == 'assess-all':
            from sentinel.evidence.assessment import HISTORICAL_OUTCOME_FIELDS, assess
            tables = engine.tables()
            summary = {'known_at': args.known_at, 'total': 0, 'readiness': Counter(), 'disposition': Counter(),
                       'conflict_kinds': Counter(), 'product_resolution': Counter(), 'events_with_conflicts': [],
                       'notice': ('Structural coverage of a stratified evidence pack. Not a population accuracy estimate, '
                                  'not an automated-closure rate, and not a judgement on any historical decision.')}
            candidates = []
            for event in tables['01_Excursion_Events']:
                result = assess(tables, event['event_id'], known_at=args.known_at)
                summary['total'] += 1
                summary['readiness'][result['conclusion']['readiness']] += 1
                summary['disposition'][result['conclusion']['disposition']] += 1
                product = next(e for e in result['entities'] if e['kind'] == 'PRODUCT')
                summary['product_resolution'][product['status']] += 1
                for conflict in result['conflicts']:
                    summary['conflict_kinds'][conflict.split(' ', 2)[0] + ' ' + conflict.split(' ', 2)[1]] += 1
                if result['conflicts']:
                    summary['events_with_conflicts'].append(result['event_id'])
                if args.compare_history and str(event.get('final_disposition', '')).strip() and result['conflicts']:
                    # Evaluation layer only: historical fields are read here, never inside assess().
                    candidates.append({'event_id': result['event_id'], 'historical_disposition': event['final_disposition'],
                                       'open_conflicts': len(result['conflicts'])})
            if args.compare_history:
                summary['review_candidates'] = {'count': len(candidates), 'examples': candidates[:25],
                                                'historical_fields_read_here_only': list(HISTORICAL_OUTCOME_FIELDS),
                                                'meaning': 'Cases whose recorded disposition coexists with unresolved evidence conflicts. '
                                                           'They are candidates for human re-review, not evidence that either side was wrong.'}
            summary['readiness'] = dict(summary['readiness'])
            summary['disposition'] = dict(summary['disposition'])
            summary['conflict_kinds'] = dict(summary['conflict_kinds'].most_common())
            summary['product_resolution'] = dict(summary['product_resolution'])
            output(summary, args.output)
        elif args.command == 'tick':
            tenants = imported_tenants(engine)
            if args.tenant not in tenants:
                raise DomainError(f'Unknown tenant {args.tenant!r}; imported tenants: {", ".join(tenants)}', 404)

            def transport(key, payload):
                if args.fail:
                    raise ConnectionError('Injected local transport outage')
            output({'stub': True, 'regulators_not_notified': True, 'results': engine.tick(args.tenant, transport)})
        elif args.command == 'report':
            tenants = imported_tenants(engine)
            states, blockers, clocks, details = Counter(), Counter(), Counter(), []
            for tenant in tenants:
                for case in engine.list_cases(tenant):
                    result = engine.get_case(tenant, case['id'])
                    states[result['state']] += 1
                    blockers.update(result['packet']['analysis']['blockers'])
                    details.append(result)
                clocks.update(item['status'] for item in engine.notifications(tenant))
            report = {'total_cases': sum(states.values()), 'states': dict(states), 'blocker_counts': dict(blockers),
                      'notification_status': dict(clocks), 'evaluated_at': engine.now(),
                      'notice': 'Structural workflow evaluation only, not clinical validity or measured accuracy.'}
            if args.output:
                report['cases'] = details
            output(report, args.output)
    except (DomainError, OSError, ValueError, sqlite3.Error, zipfile.BadZipFile, ParseError, DefusedXmlException) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
