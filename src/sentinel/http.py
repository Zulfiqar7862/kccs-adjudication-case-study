"""Loopback HTTP adapter. Static bearer identities are a local-only authentication stub."""
import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .evidence import sops_as_at
from .service import DomainError

MAX_BODY = 256 * 1024


def make_server(engine, credentials, host='127.0.0.1', port=0):
    if host not in {'127.0.0.1', 'localhost'}:
        raise ValueError('Prototype is loopback-only; deploy behind real identity and TLS before exposing it')
    if not credentials or any(not isinstance(token, str) or len(token) < 16 or
                              not isinstance(p, dict) or set(p) != {'tenant', 'actor', 'role'} or
                              not all(isinstance(v, str) and v.strip() for v in p.values())
                              for token, p in credentials.items()):
        raise ValueError('Credentials need tokens of at least 16 characters and tenant/actor/role identities')

    class Handler(BaseHTTPRequestHandler):
        server_version = 'SentinelLocal/0.1'

        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, fmt, *args):
            # Do not log bearer tokens, case IDs or source content.
            pass

        def respond(self, status, value):
            data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)
            if status == 413:
                # Send a complete rejection before closing a socket with an unread body.
                self.wfile.flush()
                self.connection.shutdown(socket.SHUT_WR)
                self.connection.settimeout(0.2)
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    self.rfile.read(min(length, 2 * MAX_BODY))
                except (OSError, ValueError):
                    pass

        def principal(self):
            header = self.headers.get('Authorization', '')
            if not header.startswith('Bearer ') or header[7:] not in credentials:
                raise DomainError('Valid bearer authentication required', 401)
            return credentials[header[7:]]

        def do_GET(self):
            self.dispatch(False)

        def do_POST(self):
            self.dispatch(True)

        def dispatch(self, post):
            try:
                parsed = urlsplit(self.path)
                parts = parsed.path.strip('/').split('/')
                if not post and parsed.path == '/health':
                    self.respond(200, {'status': 'ok', 'mode': 'local-prototype'})
                    return
                principal = self.principal()
                tenant = principal['tenant']
                if post:
                    if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                        raise DomainError('Content-Type must be application/json', 415)
                    if self.headers.get('Transfer-Encoding'):
                        raise DomainError('Chunked request bodies are unsupported', 400)
                    try:
                        length = int(self.headers.get('Content-Length', '-1'))
                    except ValueError as exc:
                        raise DomainError('Invalid Content-Length', 400) from exc
                    if length < 0:
                        raise DomainError('Content-Length required', 411)
                    if length > MAX_BODY:
                        raise DomainError('Request body too large', 413)
                    try:
                        body = json.loads(self.rfile.read(length), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                    except (ValueError, UnicodeDecodeError) as exc:
                        raise DomainError('Invalid JSON', 400) from exc
                    if not isinstance(body, dict):
                        raise DomainError('JSON body must be an object', 400)
                    if len(parts) == 3 and parts[0] == 'cases':
                        version = body.pop('expected_version', None)
                        result = engine.command(principal, parts[1], parts[2], body,
                                                self.headers.get('Idempotency-Key'), version)
                    else:
                        raise DomainError('Route not found', 404)
                elif parts == ['cases']:
                    result = engine.list_cases(tenant)
                elif len(parts) == 2 and parts[0] == 'cases':
                    result = engine.get_case(tenant, parts[1])
                elif len(parts) == 3 and parts[0] == 'cases' and parts[2] == 'audit':
                    result = engine.export(tenant, parts[1])
                elif parts == ['notifications']:
                    result = engine.notifications(tenant)
                elif parts == ['sops']:
                    query = parse_qs(parsed.query)
                    if 'valid_at' not in query:
                        raise DomainError('valid_at is required', 400)
                    result = sops_as_at(engine.tables(), tenant, query['valid_at'][0], query.get('known_at', [None])[0])
                else:
                    raise DomainError('Route not found', 404)
                self.respond(200, result)
            except DomainError as exc:
                self.respond(exc.status, {'error': str(exc)})
            except (ValueError, TypeError, KeyError):
                self.respond(400, {'error': 'Malformed request or timestamp'})
            except Exception:
                self.respond(500, {'error': 'Internal error; no successful operation should be assumed'})

    return ThreadingHTTPServer((host, port), Handler)
