"""Transactional case workflow. Index candidates never authorize a disposition."""
import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from sentinel import __version__
from sentinel.evidence import analysis as evidence
from sentinel.ingestion import workbook

DISPOSITIONS = {'RELEASE', 'RELEASE_WITH_NOTE', 'QUARANTINE', 'REWORK', 'RETURN', 'DESTROY'}
KINDS = {'SOP', 'STABILITY', 'TELEMETRY', 'IDENTITY', 'BATCH', 'CONTRACT', 'OTHER'}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def utcnow():
    return datetime.now(timezone.utc)


class DomainError(Exception):
    def __init__(self, message, status=422):
        super().__init__(message)
        self.status = status


class Engine:
    def __init__(self, path, clock=utcnow):
        self.path = str(path)
        self.clock = clock
        with self.connection() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS imports (
                    hash TEXT PRIMARY KEY, observed_at TEXT NOT NULL, tables_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS cases (
                    tenant TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
                    version INTEGER NOT NULL, state TEXT NOT NULL, source_json TEXT NOT NULL,
                    import_hash TEXT NOT NULL REFERENCES imports(hash),
                    PRIMARY KEY(tenant,id));
                CREATE TABLE IF NOT EXISTS revisions (
                    tenant TEXT NOT NULL, case_id TEXT NOT NULL, revision INTEGER NOT NULL,
                    packet_json TEXT NOT NULL, PRIMARY KEY(tenant,case_id,revision),
                    FOREIGN KEY(tenant,case_id) REFERENCES cases(tenant,id));
                CREATE TABLE IF NOT EXISTS audit (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT NOT NULL, case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL, at TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
                    payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS idempotency (
                    tenant TEXT NOT NULL, key TEXT NOT NULL, request_hash TEXT NOT NULL,
                    result_json TEXT NOT NULL, PRIMARY KEY(tenant,key));
                CREATE TABLE IF NOT EXISTS obligations (
                    tenant TEXT NOT NULL, case_id TEXT NOT NULL, alert_at TEXT NOT NULL,
                    deadline TEXT, receipt_json TEXT, PRIMARY KEY(tenant,case_id));
                CREATE TABLE IF NOT EXISTS outbox (
                    tenant TEXT NOT NULL, case_id TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                    delivered_at TEXT, last_error TEXT, PRIMARY KEY(tenant,case_id));
            ''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise

    def now(self):
        value = self.clock()
        if value.tzinfo is None:
            raise ValueError('Clock must be timezone-aware')
        return value.astimezone(timezone.utc).isoformat()

    def _audit(self, db, tenant, case_id, revision, actor, action, payload):
        previous = db.execute('SELECT hash FROM audit WHERE tenant=? AND case_id=? ORDER BY seq DESC LIMIT 1',
                              (tenant, case_id)).fetchone()
        entry = dict(tenant=tenant, case_id=case_id, revision=revision, at=self.now(), actor=actor,
                     action=action, payload=payload, previous_hash=previous['hash'] if previous else '')
        db.execute('INSERT INTO audit(tenant,case_id,revision,at,actor,action,payload_json,previous_hash,hash) VALUES(?,?,?,?,?,?,?,?,?)',
                   (tenant, case_id, revision, entry['at'], actor, action, canonical(payload), entry['previous_hash'], digest(entry)))

    def ingest(self, path):
        tables = workbook.load(path)
        required = {'01_Excursion_Events', '02_Product_Master', '05_SOP_Index', '06_Stability_Index', '12_Tenant_Constraints'}
        if not required <= tables.keys():
            raise DomainError('Workbook is missing required sheets: ' + ', '.join(sorted(required - tables.keys())))
        event_fields = {'event_id', 'tenant_code', 'alert_ts_utc', 'excursion_start_utc'}
        if not tables['01_Excursion_Events']:
            raise DomainError('Workbook must contain at least one event')
        if any(not event_fields <= event.keys() for event in tables['01_Excursion_Events']):
            raise DomainError('Event rows are missing required identity or timestamp columns')
        source_hash = workbook.sha256(path)
        tables['_observed_at'] = self.now()
        events = tables['01_Excursion_Events']
        with self.transaction() as db:
            if db.execute('SELECT 1 FROM imports WHERE hash=?', (source_hash,)).fetchone():
                return {'import_hash': source_hash, 'created': 0, 'replayed': True}
            if db.execute('SELECT 1 FROM imports LIMIT 1').fetchone():
                raise DomainError('Only one workbook snapshot is supported; use a new database for another snapshot', 409)
            # Import time records when this local system learned the snapshot.
            db.execute('INSERT INTO imports VALUES(?,?,?)', (source_hash, tables['_observed_at'], canonical(tables)))
            for event in events:
                tenant, case_id = event['tenant_code'], event['event_id']
                if not tenant or not case_id:
                    raise DomainError('Missing tenant or event id; entire import rejected')
                if db.execute('SELECT 1 FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone():
                    raise DomainError('Changed source event requires explicit reconciliation, not overwrite', 409)
                packet = dict(analysis=evidence.analyze(tables, event), artifacts=[], review=None, signatures=[], disposition=None,
                              engine_version=__version__, source_hash=source_hash)
                db.execute('INSERT INTO cases VALUES(?,?,?,?,?,?,?)',
                           (tenant, case_id, 1, 1, 'WAITING_EVIDENCE', canonical(event), source_hash))
                db.execute('INSERT INTO revisions VALUES(?,?,?,?)', (tenant, case_id, 1, canonical(packet)))
                self._audit(db, tenant, case_id, 1, 'importer', 'IMPORTED',
                            {'import_hash': source_hash, 'source_row': event['_row'], 'analysis': packet['analysis']})
                reportable = event.get('regulator_reportable', '').strip()
                if reportable != 'N':
                    start = evidence.parse_time(event['alert_ts_utc'])
                    window = event.get('reg_window_hours', '')
                    try:
                        hours = float(window)
                        if not 0 < hours <= 24 * 365:
                            raise ValueError()
                        deadline = (start + timedelta(hours=hours)).isoformat()
                    except (ValueError, TypeError, OverflowError):
                        deadline = None
                    db.execute('INSERT INTO obligations VALUES(?,?,?,?,NULL)', (tenant, case_id, start.isoformat(), deadline))
                    db.execute('INSERT INTO outbox(tenant,case_id) VALUES(?,?)', (tenant, case_id))
            return {'import_hash': source_hash, 'created': len(events), 'replayed': False}

    def _case(self, db, tenant, case_id):
        row = db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone()
        if row is None:
            raise DomainError('Case not found', 404)
        return row

    def _packet(self, db, row):
        return json.loads(db.execute('SELECT packet_json FROM revisions WHERE tenant=? AND case_id=? AND revision=?',
                                    (row['tenant'], row['id'], row['revision'])).fetchone()[0])

    def get_case(self, tenant, case_id):
        with self.connection() as db:
            row = self._case(db, tenant, case_id)
            return dict(id=case_id, tenant=tenant, revision=row['revision'], version=row['version'], state=row['state'],
                        packet=self._packet(db, row))

    def list_cases(self, tenant):
        with self.connection() as db:
            return [dict(row) for row in db.execute('SELECT id,revision,version,state FROM cases WHERE tenant=? ORDER BY id', (tenant,))]

    def tables(self):
        with self.connection() as db:
            rows = db.execute('SELECT tables_json FROM imports ORDER BY observed_at DESC').fetchall()
            if not rows:
                raise DomainError('No workbook imported', 409)
            if len(rows) != 1:
                raise DomainError('Multiple snapshots require an explicit import selection', 409)
            return json.loads(rows[0][0])

    def command(self, principal, case_id, action, body, key, expected_version):
        tenant, actor, role = principal['tenant'], principal['actor'], principal['role']
        if not isinstance(key, str) or not 1 <= len(key) <= 200:
            raise DomainError('An Idempotency-Key of 1–200 characters is required', 400)
        if type(expected_version) is not int:
            raise DomainError('expected_version must be an integer', 400)
        request_hash = digest([principal, case_id, action, body, expected_version])
        with self.transaction() as db:
            old = db.execute('SELECT * FROM idempotency WHERE tenant=? AND key=?', (tenant, key)).fetchone()
            if old:
                if old['request_hash'] != request_hash:
                    raise DomainError('Idempotency key already used for another request', 409)
                return json.loads(old['result_json'])
            row = self._case(db, tenant, case_id)
            if row['version'] != expected_version:
                raise DomainError('Stale case version; reload before acting', 409)
            packet = self._packet(db, row)
            revision, state = row['revision'], row['state']
            if action == 'evidence':
                self._role(role, {'reviewer'})
                if state == 'DISPOSED':
                    raise DomainError('Reopen a signed case before changing evidence', 409)
                kind = body.get('kind')
                if kind not in KINDS:
                    raise DomainError('Unsupported evidence kind')
                content = self._text(body, 'content', 200000)
                source_ref = self._text(body, 'source_ref', 2000)
                artifact = dict(id=f'E{len(packet["artifacts"]) + 1}', kind=kind, content=content,
                                source_ref=source_ref, sha256=hashlib.sha256(content.encode()).hexdigest(),
                                recorded_at=self.now(), recorded_by=actor)
                packet['artifacts'].append(artifact)
                packet['review'], packet['signatures'] = None, []
                state = 'WAITING_EVIDENCE'
                payload = artifact
            elif action == 'review':
                self._role(role, {'reviewer'})
                if state == 'DISPOSED':
                    raise DomainError('Case is already signed', 409)
                resolutions = body.get('resolutions')
                blockers = set(packet['analysis']['blockers'])
                if not isinstance(resolutions, dict) or set(resolutions) != blockers:
                    raise DomainError('Every blocker needs an explicit human evidence resolution')
                ids = {x['id'] for x in packet['artifacts']}
                for refs in resolutions.values():
                    if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or x not in ids for x in refs):
                        raise DomainError('Each resolution must reference recorded evidence IDs')
                if not ids:
                    raise DomainError('Source evidence is required')
                required_kinds = {'SOP', 'STABILITY', 'TELEMETRY', 'IDENTITY', 'BATCH', 'CONTRACT'}
                if not required_kinds <= {x['kind'] for x in packet['artifacts']}:
                    raise DomainError('SOP, STABILITY, TELEMETRY, IDENTITY, BATCH and CONTRACT evidence required')
                packet['review'] = dict(actor=actor, at=self.now(), resolutions=resolutions,
                                        note=self._text(body, 'note', 5000),
                                        attestation='Human attests applicability, completeness and authenticity; software does not validate document meaning')
                packet['signatures'] = []
                state, payload = 'READY_FOR_REVIEW', packet['review']
            elif action == 'sign':
                self._role(role, {'signer', 'site_qa', 'corporate_qa'})
                if state != 'READY_FOR_REVIEW' or not packet['review']:
                    raise DomainError('Evidence review must finish before signing', 409)
                disposition = body.get('disposition')
                if disposition not in DISPOSITIONS:
                    raise DomainError('Invalid disposition')
                rationale = self._text(body, 'rationale', 5000)
                constraint = next((r for r in json.loads(db.execute('SELECT tables_json FROM imports WHERE hash=?',
                                  (row['import_hash'],)).fetchone()[0])['12_Tenant_Constraints'] if r['tenant_code'] == tenant), None)
                if constraint is None:
                    raise DomainError('Unknown tenant signatory policy; manual governance required')
                dual = bool(re.search(r'\bdual\b', constraint['who_signs_a_disposition'], re.IGNORECASE))
                allowed = {'site_qa', 'corporate_qa'} if dual else {'signer'}
                self._role(role, allowed)
                if actor == packet['review']['actor']:
                    raise DomainError('Evidence reviewer cannot sign their own packet', 403)
                signatures = packet['signatures']
                if any(s['actor'] == actor or s['role'] == role for s in signatures):
                    raise DomainError('Independent approvers required', 409)
                if any(s['disposition'] != disposition for s in signatures):
                    raise DomainError('Approvers disagree; review the evidence again', 409)
                payload = dict(actor=actor, role=role, disposition=disposition, rationale=rationale, at=self.now(),
                               evidence_hash=digest({'analysis': packet['analysis'], 'artifacts': packet['artifacts'], 'review': packet['review']}))
                signatures.append(payload)
                if {s['role'] for s in signatures} == allowed:
                    state = 'DISPOSED'
                    packet['disposition'] = disposition
            elif action == 'reopen':
                self._role(role, {'reviewer'})
                if state != 'DISPOSED':
                    raise DomainError('Only disposed cases can be reopened', 409)
                payload = {'reason': self._text(body, 'reason', 5000), 'prior_revision': revision}
                revision += 1
                # Old artifacts remain accessible in prior immutable revision, never silently re-attested.
                packet = dict(analysis=packet['analysis'], artifacts=[], review=None, signatures=[], disposition=None,
                              engine_version=__version__, source_hash=row['import_hash'], reopened_for=payload['reason'])
                state = 'WAITING_EVIDENCE'
                db.execute('INSERT INTO revisions VALUES(?,?,?,?)', (tenant, case_id, revision, canonical(packet)))
            elif action == 'notify':
                self._role(role, {'regulatory'})
                obligation = db.execute('SELECT * FROM obligations WHERE tenant=? AND case_id=?', (tenant, case_id)).fetchone()
                if obligation is None:
                    raise DomainError('No notification obligation exists', 409)
                if obligation['receipt_json']:
                    raise DomainError('Receipt already recorded; correction requires governance review', 409)
                try:
                    sent_at = evidence.parse_time(self._text(body, 'sent_at', 100))
                except ValueError as exc:
                    raise DomainError('Invalid sent_at timestamp') from exc
                if sent_at < evidence.parse_time(obligation['alert_at']) or sent_at > evidence.parse_time(self.now()):
                    raise DomainError('Receipt time must be between alert and current time')
                payload = dict(receipt=self._text(body, 'receipt', 5000), sent_at=sent_at.isoformat(), actor=actor,
                               recorded_at=self.now(), verification='Human-attested external receipt, not independently verified')
                db.execute('UPDATE obligations SET receipt_json=? WHERE tenant=? AND case_id=?', (canonical(payload), tenant, case_id))
            else:
                raise DomainError('Unknown command', 404)
            version = row['version'] + 1
            db.execute('UPDATE revisions SET packet_json=? WHERE tenant=? AND case_id=? AND revision=?',
                       (canonical(packet), tenant, case_id, revision))
            db.execute('UPDATE cases SET revision=?,version=?,state=? WHERE tenant=? AND id=?',
                       (revision, version, state, tenant, case_id))
            self._audit(db, tenant, case_id, revision, actor, action.upper(), payload)
            result = dict(id=case_id, tenant=tenant, revision=revision, version=version, state=state)
            db.execute('INSERT INTO idempotency VALUES(?,?,?,?)', (tenant, key, request_hash, canonical(result)))
            return result

    @staticmethod
    def _role(role, allowed):
        if role not in allowed:
            raise DomainError('Role is not authorized for this operation', 403)

    @staticmethod
    def _text(body, key, limit):
        value = body.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise DomainError(f'{key} must be non-empty text, at most {limit} characters')
        return value

    def notifications(self, tenant):
        now = evidence.parse_time(self.now())
        with self.connection() as db:
            result = []
            for row in db.execute('SELECT * FROM obligations WHERE tenant=? ORDER BY deadline,case_id', (tenant,)):
                item = dict(row)
                receipt = json.loads(item.pop('receipt_json')) if row['receipt_json'] else None
                deadline = evidence.parse_time(row['deadline']) if row['deadline'] else None
                if deadline is None:
                    status = 'POLICY_REQUIRED'
                elif receipt:
                    status = 'NOTIFIED_ON_TIME' if evidence.parse_time(receipt['sent_at']) <= deadline else 'NOTIFIED_LATE'
                else:
                    status = 'OVERDUE' if now > deadline else 'DUE_SOON' if now >= deadline - timedelta(hours=24) else 'OPEN'
                item.update(status=status, receipt=receipt)
                result.append(item)
            return result

    def tick(self, tenant, transport):
        """Deliver internal reminders at least once; never mark regulatory filing complete."""
        with self.connection() as db:
            rows = db.execute(
                'SELECT o.* FROM outbox o JOIN obligations n ON o.tenant=n.tenant AND o.case_id=n.case_id '
                'WHERE o.tenant=? AND o.delivered_at IS NULL AND n.receipt_json IS NULL ORDER BY n.deadline,o.case_id', (tenant,)).fetchall()
        results = []
        for row in rows:
            key = f'{tenant}:{row["case_id"]}:notification-required'
            error = None
            try:
                transport(key, {'tenant': tenant, 'case_id': row['case_id'], 'type': 'NOTIFICATION_REQUIRED'})
            except Exception:
                error = 'Delivery failed; retry required'
            # Network calls never hold the case writer lock. Consumers deduplicate this stable key.
            with self.transaction() as db:
                db.execute('UPDATE outbox SET attempts=attempts+1,delivered_at=?,last_error=? '
                           'WHERE tenant=? AND case_id=? AND delivered_at IS NULL',
                           (None if error else self.now(), error, tenant, row['case_id']))
            results.append({'id': row['case_id'], 'delivered': error is None})
        return results

    def export(self, tenant, case_id):
        with self.connection() as db:
            row = self._case(db, tenant, case_id)
            revisions = [dict(revision=r['revision'], packet=json.loads(r['packet_json'])) for r in db.execute(
                'SELECT * FROM revisions WHERE tenant=? AND case_id=? ORDER BY revision', (tenant, case_id))]
            entries = []
            for item in db.execute('SELECT * FROM audit WHERE tenant=? AND case_id=? ORDER BY seq', (tenant, case_id)):
                entry = dict(item)
                entry['payload'] = json.loads(entry.pop('payload_json'))
                entries.append(entry)
            result = dict(tenant=tenant, case_id=case_id, current_revision=row['revision'], state=row['state'],
                          source_hash=row['import_hash'], source=json.loads(row['source_json']), revisions=revisions, audit=entries,
                          notice='Contains historical labels as source only, never used as decision evidence. Hash chain is not a qualified electronic signature or WORM store.')
            result['manifest_hash'] = digest(result)
            return result


def verify_export(bundle):
    """Detect accidental modification; an external trusted hash is needed against privileged rewriting."""
    body = dict(bundle)
    manifest = body.pop('manifest_hash', None)
    if digest(body) != manifest:
        return False
    previous = ''
    for item in body['audit']:
        entry = {k: v for k, v in item.items() if k not in {'seq', 'hash'}}
        if entry['previous_hash'] != previous or digest(entry) != item['hash']:
            return False
        previous = item['hash']
    for revision in body['revisions']:
        for artifact in revision['packet']['artifacts']:
            if hashlib.sha256(artifact['content'].encode()).hexdigest() != artifact['sha256']:
                return False
    return bool(body['audit'])
