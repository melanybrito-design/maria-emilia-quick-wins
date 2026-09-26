import argparse
import json
import sys

from config import ROOT, Rules
from excel_manager import InputError, sample_book
from journal import Journal, worker_lock
from runner import simulate

def positive(value):
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError('Use un entero positivo.')
    return n

def main(argv=None):
    parser = argparse.ArgumentParser(description='CAFI · diagnóstico local y simulación 0.1.0')
    parser.add_argument('--input')
    parser.add_argument('--sheet',default='Hoja 1')
    parser.add_argument('--code-length',type=positive,default=10)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--dry-run',action='store_true')
    modes.add_argument('--simulate',action='store_true')
    modes.add_argument('--execute',action='store_true')
    modes.add_argument('--inspect-ui',action='store_true')
    modes.add_argument('--serve',action='store_true')
    modes.add_argument('--create-samples',action='store_true')
    parser.add_argument('--resume')
    parser.add_argument('--limit',type=positive)
    parser.add_argument('--synthetic-confirmed',action='store_true')
    parser.add_argument('--scenario',default='success',choices=['success','timeout','reject','ok_failure','focus_loss','session_loss','readback_mismatch','print_failure'])
    parser.add_argument('--pid',type=positive)
    parser.add_argument('--backend',choices=['uia','win32'],default='uia')
    parser.add_argument('--data-dir',type=str,default=str(ROOT/'data'))
    parser.add_argument('--port',type=positive,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    args = parser.parse_args(argv)
    try:
        from pathlib import Path
        if args.execute:
            from cafi_bot import real_adapter
            real_adapter()
        if args.serve:
            from server import serve
            serve(args.data_dir,args.port,not args.no_browser)
            return 0
        if args.inspect_ui:
            from inspect_windows import inspect_ui
            out = Path(args.data_dir)/'inspeccion'/f'controles_{args.backend}.json'
            print(json.dumps(inspect_ui(out,args.pid,args.backend),ensure_ascii=False,indent=2))
            return 0
        if args.create_samples:
            folder = ROOT/'ejemplos'
            folder.mkdir(exist_ok=True)
            for name,bad in [('lote_sintetico.xlsx',False),('lote_con_incidencias.xlsx',True)]:
                (folder/name).write_bytes(sample_book(bad))
            print('Ejemplos sintéticos disponibles en ejemplos/.')
            return 0
        if not args.input and not args.resume:
            parser.error('Indique --input, --resume o --serve.')
        journal = Journal(args.data_dir)
        with worker_lock(journal.root):
            journal.recover()
            if args.resume:
                run = journal.get(args.resume)
                if args.input:
                    from excel_manager import digest
                    if digest(Path(args.input).read_bytes()) != run['hash']:
                        raise InputError('El archivo no coincide con el hash de origen del lote.')
            else:
                path = Path(args.input)
                if path.suffix.lower() != '.xlsx':
                    raise InputError('Seleccione un archivo .xlsx.')
                run = journal.create(path.read_bytes(),Rules(args.code_length,args.sheet))
        code = 0
        if args.simulate:
            code = simulate(journal,run['id'],synthetic_confirmed=args.synthetic_confirmed,scenario=args.scenario,limit=args.limit)
        run = journal.get(run['id'])
        print(json.dumps({'run_id':run['id'],'mode':'SIMULACION' if args.simulate else 'DIAGNOSTICO','counts':run['counts'],'blank_rows':run['blank'],'total':run['total']},ensure_ascii=False,indent=2))
        if any(r['state']=='REQUIERE_REVISION' for r in run['rows']):
            return 3
        return code or (2 if run['counts'].get('ERROR') else 0)
    except (ValueError,OSError) as exc:
        # No imprimir texto de celdas ni excepciones con rutas de usuario.
        print(str(exc) if isinstance(exc,ValueError) else 'No se pudo acceder a un archivo o puerto. Cierre Excel y revise permisos.',file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
