"""Entrada compatible para el flujo local real; el simulador se mantiene separado."""
from config import ROOT, VERSION
from windows_rpa import RpaError, load_profile

ConnectionPending = RpaError

def connection_status(attached=False, profile_path=None):
    try:
        load_profile(profile_path or ROOT / 'data' / 'perfil_cafi.json')
        configured = True
    except RpaError:
        configured = False
    return {'ready': bool(attached and configured), 'attached': bool(attached),
            'kind': 'windows_application', 'version': VERSION,
            'message': 'Mapa disponible para comprobar en CAFI.' if configured else 'Configure los controles observados de CAFI en Windows.'}

def start_attached_workflow(window_handle, workbook, **options):
    if not window_handle or not workbook:
        raise ConnectionPending('Selecciona la ventana de CAFI y el Excel.')
    from real_workflow import start_workflow
    return start_workflow(window_handle, workbook,
        options.pop('profile_path', ROOT / 'data' / 'perfil_cafi.json'),
        options.pop('data_root', ROOT / 'data' / 'operacion'), **options)
