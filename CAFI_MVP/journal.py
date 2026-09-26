"""SQLite atómico y bloqueo del SO: el cierre del proceso libera el bloqueo."""
import json
import os
import sqlite3
import uuid
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from config import Rules
from excel_manager import digest, export_results, validate

def now():
    return datetime.now(timezone.utc).isoformat()

class BusyError(ValueError):
    pass

@contextmanager
def worker_lock(root):
    path = Path(root) / 'worker.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path, 'a+b')
    handle.seek(0)
    if path.stat().st_size == 0:
        handle.write(b'0')
        handle.flush()
    handle.seek(0)
    locked = False
    try:
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except (OSError, BlockingIOError) as exc:
            raise BusyError('Ya hay un lote en ejecución. Espere o deténgalo desde su ventana.') from exc
        yield
    finally:
        if locked:
            handle.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()

class Journal:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, hash TEXT NOT NULL, sheet TEXT NOT NULL,
                    rules TEXT NOT NULL, created TEXT NOT NULL, status TEXT NOT NULL,
                    blank INTEGER NOT NULL, stop INTEGER NOT NULL DEFAULT 0,
                    message TEXT NOT NULL DEFAULT '', schema_version INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS rows (
                    run_id TEXT NOT NULL, row_no INTEGER NOT NULL, fingerprint TEXT NOT NULL,
                    state TEXT NOT NULL, message TEXT NOT NULL, stage TEXT NOT NULL,
                    transaction_id TEXT, PRIMARY KEY(run_id,row_no)
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY, run_id TEXT NOT NULL, row_no INTEGER,
                    at TEXT NOT NULL, state TEXT NOT NULL, stage TEXT NOT NULL,
                    message TEXT NOT NULL
                );
            ''')

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.root / 'journal.sqlite3', timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA synchronous=FULL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def create(self, content, rules):
        diagnosis = validate(content, rules)
        rules_json = json.dumps(diagnosis['rules'],sort_keys=True)
        with self.db() as db:
            previous = db.execute('SELECT id FROM runs WHERE hash=? AND rules=? ORDER BY created DESC LIMIT 1',(diagnosis['hash'],rules_json)).fetchone()
            if previous:
                return self.get(previous['id'])
        run_id = uuid.uuid4().hex
        folder = self.root / run_id
        folder.mkdir()
        source = folder / 'origen.xlsx'
        with open(source,'xb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        with self.db() as db:
            db.execute('INSERT INTO runs(id,hash,sheet,rules,created,status,blank) VALUES (?,?,?,?,?,?,?)',
                       (run_id,diagnosis['hash'],rules.sheet,rules_json,now(),'REVISADO',diagnosis['blank_rows']))
            for row in diagnosis['rows']:
                state = 'ERROR' if row['issues'] else 'PENDIENTE'
                msg = ' '.join(row['issues']) if row['issues'] else 'Datos válidos. Destinatario pendiente de verificación en CAFI.'
                db.execute('INSERT INTO rows VALUES (?,?,?,?,?,?,?)',(run_id,row['row'],row['fingerprint'],state,msg,'DIAGNOSTICO',None))
            db.execute('INSERT INTO events(run_id,at,state,stage,message) VALUES (?,?,?,?,?)',(run_id,now(),'REVISADO','INICIO','Diagnóstico local; sin conexión a CAFI.'))
        self.export(run_id)
        return self.get(run_id)

    def metadata(self, run_id):
        if not isinstance(run_id,str) or len(run_id)!=32 or any(c not in '0123456789abcdef' for c in run_id):
            raise ValueError('Identificador de lote inválido.')
        with self.db() as db:
            run = db.execute('SELECT * FROM runs WHERE id=?',(run_id,)).fetchone()
        if run is None:
            raise ValueError('No se encontró ese lote en esta computadora.')
        if run['schema_version'] != 1:
            raise ValueError('Versión de bitácora incompatible.')
        return dict(run)

    def get(self, run_id):
        run = self.metadata(run_id)
        content = (self.root / run_id / 'origen.xlsx').read_bytes()
        if digest(content) != run['hash']:
            raise ValueError('La copia de origen cambió. Lote bloqueado para conciliación.')
        diagnosis = validate(content,Rules(**json.loads(run['rules'])))
        with self.db() as db:
            states = {r['row_no']:dict(r) for r in db.execute('SELECT * FROM rows WHERE run_id=?',(run_id,))}
            events = [dict(r) for r in db.execute('SELECT at,row_no,state,stage,message FROM events WHERE run_id=? ORDER BY id DESC LIMIT 100',(run_id,))]
        rows = []
        for row in diagnosis['rows']:
            stored = states.get(row['row'])
            if stored is None or stored['fingerprint'] != row['fingerprint']:
                raise ValueError('El contenido ya no coincide con la bitácora.')
            rows.append({**row,**stored})
        return {**run,'rules':json.loads(run['rules']),'rows':rows,'counts':dict(Counter(r['state'] for r in rows)), 'total':len(rows),'events':events}

    def transition(self, run_id, row_no, state, stage, message, transaction_id=None):
        with self.db() as db:
            old = db.execute('SELECT state FROM rows WHERE run_id=? AND row_no=?',(run_id,row_no)).fetchone()
            if old is None:
                raise ValueError('Fila desconocida.')
            if old['state'] in ('PROCESADO','REQUIERE_REVISION') and old['state'] != state:
                raise ValueError('No se permite reabrir una fila confirmada o incierta.')
            db.execute('UPDATE rows SET state=?,stage=?,message=?,transaction_id=COALESCE(?,transaction_id) WHERE run_id=? AND row_no=?',
                       (state,stage,message,transaction_id,run_id,row_no))
            db.execute('INSERT INTO events(run_id,row_no,at,state,stage,message) VALUES (?,?,?,?,?,?)',
                       (run_id,row_no,now(),state,stage,message))

    def status(self, run_id, status, message):
        with self.db() as db:
            db.execute('UPDATE runs SET status=?,message=? WHERE id=?',(status,message,run_id))
            db.execute('INSERT INTO events(run_id,at,state,stage,message) VALUES (?,?,?,?,?)',(run_id,now(),status,'LOTE',message))

    def stop(self, run_id, value=True):
        self.metadata(run_id)
        with self.db() as db:
            db.execute('UPDATE runs SET stop=? WHERE id=?',(int(value),run_id))

    def recover(self):
        # Invocar exclusivamente mientras se tiene worker_lock.
        with self.db() as db:
            pending = list(db.execute("SELECT run_id,row_no FROM rows WHERE state='EN_PROCESO'"))
            active = list(db.execute("SELECT id FROM runs WHERE status='EN_EJECUCION'"))
        for row in pending:
            self.transition(row['run_id'],row['row_no'],'REQUIERE_REVISION','INTERRUMPIDO','Intento interrumpido; requiere conciliación, sin reintento automático.')
        for run in active:
            self.status(run['id'],'DETENIDO','La aplicación se cerró durante el lote. Revise la bitácora.')

    def export(self, run_id):
        run = self.get(run_id)
        folder = self.root / run_id
        content = export_results((folder/'origen.xlsx').read_bytes(),Rules(**run['rules']),run['rows'],run_id)
        temporary = folder / ('resultados-' + uuid.uuid4().hex + '.tmp')
        try:
            with open(temporary,'xb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary,folder/'resultados_simulacion.xlsx')
        finally:
            temporary.unlink(missing_ok=True)
        return folder/'resultados_simulacion.xlsx'

    def history(self):
        with self.db() as db:
            return [dict(r) for r in db.execute('SELECT id,created,status,message FROM runs ORDER BY created DESC LIMIT 50')]

    def support_report(self, run_id):
        run = self.get(run_id)
        # Sin códigos, nombres, títulos, detalles, ruta de usuario ni hash de contenido.
        return {k:run[k] for k in ['id','created','status','message','counts','total','blank','events']}
