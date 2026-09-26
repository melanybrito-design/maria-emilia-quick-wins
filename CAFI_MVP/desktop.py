"""Compatibilidad: la entrada de escritorio ahora utiliza Qt Widgets nativo."""
from native_app import run_desktop

if __name__ == '__main__':
    raise SystemExit(run_desktop())
