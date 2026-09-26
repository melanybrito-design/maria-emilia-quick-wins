"""Entrada sin consola. No escribe trazas ni credenciales al fallar."""
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.coinit_flags = 2  # COM STA consistente para inventario y trabajador Windows.
sys.path.insert(0, str(root))

if __name__ == '__main__':
    try:
        import site
        package_dir = root / 'runtime' / 'Lib' / 'site-packages'
        if os.name == 'nt' and package_dir.exists():
            site.addsitedir(str(package_dir))
        from native_app import run_desktop
        run_desktop()
    except Exception:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,
                'No se pudo abrir la ventana de CAFI. Comprueba que extrajiste todo el ZIP. '
                'Ejecuta DIAGNOSTICO_WINDOWS.bat y consulta LEEME_WINDOWS.md. '
                'El asistente no pudo arrancar.',
                'CAFI · UEES', 0x10)
        else:
            raise
