"""Command-line entry point for local development and authorized workbook replay."""
import argparse
import json
import os
import secrets
import sqlite3
import zipfile
from xml.etree.ElementTree import ParseError

from defusedxml.common import DefusedXmlException
from collections import Counter
from pathlib import Path

from .service import DomainError, Engine, verify_export


def output(value, path=None):
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


def main():
    parser = argparse.ArgumentParser(description='Local evidence-first adjudication workflow')
    parser.add_argument('--db', default='artifacts/sentinel.db', help='Local SQLite path (default: artifacts/sentinel.db)')
    commands = parser.add_subparsers(dest='command', required=True)
    sample = commands.add_parser('sample', help='Generate a wholly fictional workbook')
    sample.add_argument('--output', default='artifacts/sample.xlsx')
    commands.add_parser('demo', help='Exercise the full HTTP lifecycle on fictional data in a temporary database')
    imp = commands.add_parser('import', help='Import one authorized workbook snapshot atomically')
    imp.add_argument('workbook')
    report = commands.add_parser('report', help='Summarize imported evidence blockers and notification clocks')
    report.add_argument('--output', help='Full report includes source-derived private data; keep it local')
    serve = commands.add_parser('serve', help='Start the authenticated loopback JSON API')
    serve.add_argument('--credentials', default='artifacts/local-credentials.json')
    serve.add_argument('--port', type=int, default=8080)
    credentials = commands.add_parser('credentials', help='Generate private local-only bearer identities')
    credentials.add_argument('--tenant', action='append', required=True)
    credentials.add_argument('--output', default='artifacts/local-credentials.json')
    export = commands.add_parser('export', help='Export a private tenant case audit bundle')
    export.add_argument('--tenant', required=True)
    export.add_argument('--case', required=True)
    export.add_argument('--output', required=True)
    verify = commands.add_parser('verify', help='Verify an exported audit bundle')
    verify.add_argument('file')
    tick = commands.add_parser('tick', help='Run internal reminder stub; never files with a regulator')
    tick.add_argument('--tenant', required=True)
    tick.add_argument('--fail', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'sample':
            from .sample import create_workbook
            create_workbook(args.output)
            output({'source': 'fictional', 'workbook': args.output})
            return
        if args.command == 'demo':
            from .demo import run_demo
            output(run_demo())
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
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
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
        path = Path(args.db)
        path.parent.mkdir(parents=True, exist_ok=True)
        engine = Engine(path)
        if args.command == 'import':
            output(engine.ingest(args.workbook))
        elif args.command == 'serve':
            from .http import make_server
            identities = json.loads(Path(args.credentials).read_text(encoding='utf-8'))
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
        elif args.command == 'tick':
            def transport(key, payload):
                if args.fail:
                    raise ConnectionError('Injected local transport outage')
            output({'stub': True, 'regulators_not_notified': True, 'results': engine.tick(args.tenant, transport)})
        elif args.command == 'report':
            tables = engine.tables()
            tenants = sorted({event['tenant_code'] for event in tables['01_Excursion_Events']})
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
