"""Construye ZIP de código y ejemplos; nunca incorpora datos de una ejecución."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / 'CAFI_MVP_Windows_v0.4.0.zip'
DIRECTORIES = {'assets', 'runtime'}
ROOT_SUFFIXES = {'.py','.pyw','.md','.txt','.bat','.exe'}
LEGACY_ROOT = {'server.py', 'main.py', 'runner.py', 'cafi_bot.py', 'desktop.py',
               'session_controller.py', 'INICIAR_MAC.command'}

def main():
    files = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        # El paquete operativo no requiere páginas HTML, incluidas las ayudas de terceros.
        if path.suffix.lower() == '.html':
            continue
        # La distribución operativa abre únicamente Qt. La antigua UI web queda en desarrollo.
        if len(relative.parts) == 1 and path.name in LEGACY_ROOT:
            continue
        if any(part in {'__pycache__','.pytest_cache','.venv','data','.playwright-cli','build'} for part in relative.parts):
            continue
        is_operator_doc = relative.as_posix() == 'docs/VALIDACION.md'
        if (len(relative.parts)==1 and (path.suffix in ROOT_SUFFIXES or path.name=='.gitignore')) or relative.parts[0] in DIRECTORIES or is_operator_doc:
            files.append((path,relative.as_posix()))
    manifest = {name:hashlib.sha256(path.read_bytes()).hexdigest() for path,name in files}
    with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED) as archive:
        for path,name in files:
            archive.write(path,'CAFI_MVP/'+name)
        archive.writestr('CAFI_MVP/MANIFEST_SHA256.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(OUTPUT) as archive:
        assert 'CAFI_MVP/CAFI.pyw' in archive.namelist()
        assert 'CAFI_MVP/runtime/pythonw.exe' in archive.namelist()
        assert not any(p.startswith('CAFI_MVP/ui/') or p.endswith('.html')
                       or p in {f'CAFI_MVP/{name}' for name in LEGACY_ROOT} for p in archive.namelist())
        assert archive.testzip() is None
        for name,expected in manifest.items():
            assert hashlib.sha256(archive.read('CAFI_MVP/'+name)).hexdigest()==expected
    print(f'{OUTPUT.name}: {len(files)} archivos, {OUTPUT.stat().st_size:,} bytes; integridad verificada.')

if __name__ == '__main__':
    main()
