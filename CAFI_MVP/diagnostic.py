"""Diagnóstico de instalación: no enumera CAFI, no lee campos ni credenciales."""
import importlib
import json
import platform
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    result = {'app_version': '0.4.0', 'system': platform.system(), 'system_release': platform.release(),
              'python': platform.python_version(), 'bits': struct.calcsize('P') * 8, 'modules': {}}
    for name in ['sqlite3', 'openpyxl', 'PySide6.QtWidgets', 'pywinauto', 'pythoncom', 'win32api', 'comtypes']:
        try:
            importlib.import_module(name)
            result['modules'][name] = 'OK'
        except Exception as exc:
            result['modules'][name] = 'ERROR: ' + type(exc).__name__
    result['checks'] = {name: (ROOT / name).is_file() for name in ['CAFI.pyw', 'native_app.py', 'windows_rpa.py', 'real_workflow.py', 'assets/cafi.ico']}
    folder = ROOT / 'data'
    folder.mkdir(exist_ok=True)
    (folder / 'diagnostico_instalacion.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    print('Resultado: data/diagnostico_instalacion.json. No contiene credenciales ni datos de estudiantes.')
    return 0 if all(v == 'OK' for v in result['modules'].values()) and all(result['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
