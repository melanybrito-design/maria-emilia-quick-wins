"""Inventario de controles, exclusivamente de lectura y por PID explícito."""
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

def inspect_ui(output, pid=None, backend='uia'):
    if platform.system() != 'Windows':
        raise ValueError('La inspección requiere Windows, en la computadora donde corre SIAC.')
    try:
        from pywinauto import Desktop
    except ImportError as exc:
        raise ValueError('Instale requirements-windows.txt con el Python del proyecto.') from exc
    desktop = Desktop(backend=backend)
    if pid is None:
        # Sin leer títulos de ventanas de otras aplicaciones.
        windows = [{'pid':w.process_id(),'handle':w.handle,'class_name':w.class_name()} for w in desktop.windows()]
        return {'backend':backend,'windows':windows,'next':'Identifique el PID de SIAC en Administrador de tareas > Detalles. Repita con --pid NUMERO.'}
    result = []
    for window in desktop.windows(process=pid):
        controls = []
        for control in [window] + window.descendants():
            info = control.element_info
            rectangle = control.rectangle()
            controls.append({'name':control.window_text(),'class_name':control.class_name(),
                             'control_type':getattr(info,'control_type',None),
                             'automation_id':getattr(info,'automation_id',None),
                             'control_id':getattr(info,'control_id',None),
                             'rectangle':[rectangle.left,rectangle.top,rectangle.right,rectangle.bottom]})
        result.append({'handle':window.handle,'controls':controls})
    if not result:
        raise ValueError('No se encontraron ventanas del PID indicado en ese backend.')
    report = {'at':datetime.now(timezone.utc).isoformat(),'backend':backend,'pid':pid,'windows':result,
              'notice':'Inventario observado; no son selectores aprobados. Puede contener texto visible de SIAC. Revisar antes de compartir.'}
    path = Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'output':str(path),'windows':len(result),'message':'Inventario escrito. No se hizo clic ni se guardaron trámites.'}
