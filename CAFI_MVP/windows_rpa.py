"""Control de CAFI por controles observados. Ningún selector viene de Panacea.

Las credenciales se escriben directamente en el control, nunca en portapapeles,
argumentos, configuración o bitácora. Los errores no incluyen valores de campos.
"""
import json
import os
import time
from pathlib import Path


class RpaError(RuntimeError):
    pass


class StopRequested(RpaError):
    pass


ROLES = {
    'username': 'Acceso · Usuario', 'password': 'Acceso · Contraseña',
    'login': 'Acceso · Ingresar', 'authenticated': 'Acceso · Indicador de sesión iniciada',
    'processes': 'Navegación · Procesos', 'procedures': 'Navegación · Trámites estudiante',
    'entry': 'Navegación · Ingreso de procesos', 'new': 'Navegación · Nuevo registro',
    'process': 'Formulario · Tipo de proceso', 'code': 'Formulario · Código del destinatario',
    'recipient': 'Formulario · Nombre resuelto por CAFI', 'title': 'Formulario · Título',
    'detail': 'Formulario · Detalle', 'priority': 'Formulario · Prioridad',
    'save': 'Formulario · Guardar', 'success_message': 'Confirmación · Mensaje de éxito',
    'success_ok': 'Confirmación · OK', 'print_destination': 'Impresión · Destino',
    'print_copies': 'Impresión · Copias', 'print_pdf': 'Impresión · Opción PDF',
    'print_button': 'Impresión · Botón Impresión', 'print_ready': 'Resultado · Indicador de reporte terminado',
    'transaction_id': 'Resultado · Código del trámite', 'gpa': 'Resultado · GPA',
    'credits': 'Resultado · Créditos aprobados', 'close_report': 'Resultado · Cerrar reporte (opcional)',
    'reset': 'Siguiente · Limpiar formulario',
}
REQUIRED = {'process', 'code', 'recipient', 'title', 'detail', 'priority', 'save',
            'success_message', 'success_ok', 'print_destination', 'print_copies',
            'print_pdf', 'print_button', 'print_ready', 'transaction_id', 'gpa', 'credits', 'reset'}


def empty_profile():
    return {'version': 1, 'backend': 'uia', 'controls': {}, 'timeout': 20,
            # SIAC/CAFI puede tardar en responder; este intervalo se aplica entre
            # acciones de navegación, confirmación, impresión y limpieza.
            'step_delay': 12,
            'process_value': '12', 'destination': 'Pantalla', 'copies': '1',
            'success_text': 'La Transacción se realizó Exitosamente...',
            'navigation': ['processes', 'procedures', 'entry', 'new']}


def validate_profile(profile, login=False):
    if profile.get('version') != 1 or profile.get('backend') not in ('uia', 'win32'):
        raise RpaError('El mapa de controles no es compatible.')
    controls = profile.get('controls', {})
    required = REQUIRED | ({'username', 'password', 'login', 'authenticated'} if login else set())
    missing = required - controls.keys()
    if missing:
        raise RpaError('Falta configurar: ' + ', '.join(ROLES[k] for k in sorted(missing)))
    if not 1 <= float(profile.get('timeout', 20)) <= 120:
        raise RpaError('El tiempo de espera debe estar entre 1 y 120 segundos.')
    if not 10 <= float(profile.get('step_delay', 12)) <= 15:
        raise RpaError('La espera entre acciones de CAFI debe estar entre 10 y 15 segundos.')
    if not str(profile.get('success_text', '')).strip():
        raise RpaError('Falta el texto exacto de la confirmación de guardado.')
    for key in ('process_value', 'destination', 'copies'):
        if not isinstance(profile.get(key), str) or not profile[key].strip():
            raise RpaError('Falta configurar el proceso o las opciones de impresión.')
    if not profile['copies'].isdigit() or int(profile['copies']) < 1:
        raise RpaError('El número de copias debe ser un entero positivo.')
    if not isinstance(profile.get('navigation', []), list) or any(
            role not in ('processes', 'procedures', 'entry', 'new') for role in profile.get('navigation', [])):
        raise RpaError('La navegación contiene un paso no admitido.')
    for role, spec in controls.items():
        if role not in ROLES or not isinstance(spec, dict):
            raise RpaError('El mapa contiene un campo desconocido.')
        selector = spec.get('selector', {})
        if not selector or set(selector) - {'auto_id', 'control_id', 'class_name', 'control_type', 'title'}:
            raise RpaError('Selector vacío o no admitido: ' + ROLES[role])
        if spec.get('scope') not in ('main', 'popup'):
            raise RpaError('Indique la ventana del control: ' + ROLES[role])
        if spec['scope'] == 'popup' and (not spec.get('window') or set(spec['window']) - {'title', 'class_name'}):
            raise RpaError('Falta identificar la ventana emergente.')
        if spec.get('action', 'click') not in ('click', 'double_click', 'right_click', 'enter'):
            raise RpaError('Acción no admitida.')
        if spec.get('write', 'text') not in ('text', 'select'):
            raise RpaError('Escritura no admitida.')
    return profile


def load_profile(path, login=False):
    try:
        profile = json.loads(Path(path).read_text(encoding='utf-8'))
        return validate_profile(profile, login)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        raise RpaError('No se pudo leer el mapa de controles. Abra Configurar CAFI.') from exc


def list_windows():
    if os.name != 'nt':
        raise RpaError('La conexión a CAFI se ejecuta en la computadora Windows donde está instalado.')
    from pywinauto import Desktop
    result = []
    for w in Desktop(backend='win32').windows(visible_only=True):
        if w.process_id() != os.getpid() and w.window_text().strip():
            result.append({'handle': w.handle, 'pid': w.process_id(),
                           'title': w.window_text(), 'class_name': w.class_name()})
    return result


def matches(control, selector):
    info = control.element_info
    actual = {'auto_id': getattr(info, 'automation_id', None),
              'control_id': getattr(info, 'control_id', None),
              'class_name': control.class_name(),
              'control_type': getattr(info, 'control_type', None), 'title': control.window_text()}
    return all(actual.get(k) == v for k, v in selector.items())


class WindowsDriver:
    def __init__(self, attached, profile, stop_event):
        if os.name != 'nt':
            raise RpaError('Ejecute este asistente en la laptop Windows que tiene CAFI abierto.')
        from pywinauto import Desktop
        self.desktop = Desktop(backend=profile['backend'])
        self.attached = dict(attached)
        self.profile = profile
        self.stop = stop_event
        self.check_identity()

    def check_identity(self):
        from pywinauto import Desktop
        try:
            w = Desktop(backend='win32').window(handle=self.attached['handle']).wrapper_object()
            if w.process_id() != self.attached['pid'] or w.class_name() != self.attached['class_name']:
                raise RpaError('La ventana seleccionada cambió. Vuelva a asociar CAFI.')
            return w
        except RpaError:
            raise
        except Exception as exc:
            raise RpaError('La ventana de CAFI se cerró o no es accesible.') from exc

    def check_stop(self):
        if self.stop.is_set():
            raise StopRequested('Detenido por la usuaria. No se enviarán nuevas acciones.')
        self.check_identity()

    def candidates(self, role):
        self.check_stop()
        spec = self.profile['controls'][role]
        if spec['scope'] == 'main':
            windows = [self.desktop.window(handle=self.attached['handle']).wrapper_object()]
        else:
            windows = [w for w in self.desktop.windows(process=self.attached['pid'], visible_only=True)
                       if matches(w, spec['window'])]
        if len(windows) > 1:
            raise RpaError('Hay más de una ventana para: ' + ROLES[role])
        found = []
        for w in windows:
            for control in [w] + w.descendants():
                if control.is_visible() and matches(control, spec['selector']):
                    found.append(control)
        if len(found) > 1:
            raise RpaError('El control es ambiguo; ajuste su mapa: ' + ROLES[role])
        return found

    def find(self, role, timeout=None):
        deadline = time.monotonic() + (self.profile.get('timeout', 20) if timeout is None else timeout)
        while True:
            found = self.candidates(role)
            if found:
                return found[0]
            if time.monotonic() >= deadline:
                raise RpaError('No se encontró: ' + ROLES[role] + '. No se repetirá la acción.')
            self.stop.wait(0.15)

    def exists(self, role):
        return role in self.profile['controls'] and bool(self.candidates(role))

    def focus(self, control):
        self.check_stop()
        top = control.top_level_parent()
        if top.process_id() != self.attached['pid']:
            raise RpaError('Se perdió la ventana de CAFI.')
        if top.is_minimized():
            top.restore()
        top.set_focus()
        import win32gui, win32process
        _, pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        if pid != self.attached['pid']:
            raise RpaError('CAFI no está en primer plano. El robot se detuvo.')
        if not top.is_enabled() or not control.is_enabled():
            raise RpaError('El control de CAFI está deshabilitado.')

    def settle(self):
        """Da tiempo a SIAC para terminar una acción antes de continuar."""
        delay = float(self.profile.get('step_delay', 12))
        if self.stop.wait(delay):
            raise StopRequested('Detenido por la usuaria. No se enviarán nuevas acciones.')
        self.check_identity()

    def click(self, role):
        control = self.find(role)
        self.focus(control)
        action = self.profile['controls'][role].get('action', 'click')
        if action == 'enter':
            control.set_focus()
            control.type_keys('{ENTER}')
        elif action == 'double_click':
            control.double_click_input()
        elif action == 'right_click':
            control.click_input(button='right')
        else:
            control.click_input()
        self.settle()

    def text(self, role):
        control = self.find(role)
        try:
            if hasattr(control, 'get_value'):
                value = control.get_value()
            elif hasattr(control, 'selected_text'):
                value = control.selected_text()
            else:
                value = control.window_text()
            return str(value).replace('\r\n', '\n').replace('\r', '\n')
        except Exception as exc:
            raise RpaError('No se pudo leer: ' + ROLES[role]) from exc

    def expect(self, role, value):
        deadline = time.monotonic() + self.profile.get('timeout', 20)
        while True:
            if self.text(role) == value:
                return
            if time.monotonic() >= deadline:
                raise RpaError('La lectura no coincide: ' + ROLES[role])
            self.stop.wait(0.15)

    def write(self, role, value, enter=False, secret=False):
        control = self.find(role)
        self.focus(control)
        try:
            if self.profile['controls'][role].get('write') == 'select':
                control.select(value)
            else:
                control.set_edit_text(value)
            if not secret:
                self.expect(role, value)
            if enter:
                control.set_focus()
                control.type_keys('{ENTER}')
                self.settle()
        except RpaError:
            raise
        except Exception as exc:
            raise RpaError('No se pudo completar: ' + ROLES[role]) from exc

    def check_pdf(self):
        control = self.find('print_pdf')
        self.focus(control)
        if hasattr(control, 'get_toggle_state'):
            if control.get_toggle_state() != 1:
                control.toggle()
            if control.get_toggle_state() != 1:
                raise RpaError('CAFI no confirmó la opción PDF.')
        elif hasattr(control, 'is_selected'):
            control.select()
            if not control.is_selected():
                raise RpaError('CAFI no confirmó la opción PDF.')
        elif hasattr(control, 'get_check_state'):
            control.check()
            if control.get_check_state() != 1:
                raise RpaError('CAFI no confirmó la opción PDF.')
        else:
            raise RpaError('La opción PDF no expone su estado. Ajuste el mapa en Windows.')

    def login(self, username, password):
        self.write('username', username, secret=True)
        self.write('password', password, secret=True)
        self.click('login')
        self.find('authenticated')

    def prepare(self, row):
        if not self.exists('process'):
            for role in self.profile.get('navigation', []):
                if role not in self.profile['controls']:
                    raise RpaError('Falta configurar la navegación: ' + ROLES.get(role, role))
                self.click(role)
        # Nunca sobrescribir un formulario que conserva datos de otra operación.
        for role in ('code', 'title', 'detail'):
            if self.text(role).strip():
                raise RpaError('El formulario contiene datos. Revíselo y déjelo vacío antes de iniciar.')
        self.write('process', str(self.profile['process_value']), enter=True)
        self.write('code', row['code'], enter=True)
        self.expect('recipient', row['name'])
        for role in ('title', 'detail', 'priority'):
            self.write(role, row[role])
        for role in ('code', 'title', 'detail', 'priority'):
            self.expect(role, row[role].replace('\r\n', '\n').replace('\r', '\n'))
        self.expect('process', str(self.profile['process_value']))
        self.expect('recipient', row['name'])
        if self.exists('success_message'):
            raise RpaError('Hay una confirmación anterior abierta. Concilie antes de continuar.')

    def save(self):
        self.click('save')  # Una sola pulsación. Una excepción nunca provoca reenvío.
        self.expect('success_message', self.profile['success_text'])

    def open_print(self):
        self.click('success_ok')
        self.write('print_destination', self.profile['destination'])
        self.write('print_copies', str(self.profile['copies']))
        self.check_pdf()
        if self.exists('print_ready'):
            raise RpaError('Hay un reporte anterior abierto. No se enviará otra impresión.')

    def print_report(self):
        self.click('print_button')
        self.find('print_ready')

    def results(self):
        result = {role: self.text(role).strip() for role in ('transaction_id', 'gpa', 'credits')}
        if not all(result.values()) or not result['transaction_id'].isdigit():
            raise RpaError('El reporte no permite leer todos los resultados; requiere revisión.')
        return result

    def reset(self):
        if 'close_report' in self.profile['controls']:
            self.click('close_report')
        self.click('reset')
        for role in ('code', 'title', 'detail'):
            self.expect(role, '')
        self.write('process', str(self.profile['process_value']), enter=True)


def inventory(attached, backend):
    """Devuelve candidatos observados para el configurador; no hace clic ni escribe."""
    import threading
    driver = WindowsDriver(attached, {'backend': backend}, threading.Event())
    items = []
    for w in driver.desktop.windows(process=attached['pid'], visible_only=True):
        for c in [w] + w.descendants():
            if not c.is_visible():
                continue
            info = c.element_info
            password = bool(getattr(info, 'is_password', False))
            name = '' if password else c.window_text()
            selector = {'class_name': c.class_name()}
            if backend == 'uia':
                if getattr(info, 'automation_id', ''):
                    selector['auto_id'] = info.automation_id
                if getattr(info, 'control_type', ''):
                    selector['control_type'] = info.control_type
            elif getattr(info, 'control_id', 0):
                selector['control_id'] = info.control_id
            # Valores variables de Edit/Combo nunca forman parte del selector.
            dynamic = password or getattr(info, 'control_type', '') in ('Edit', 'ComboBox') or any(
                k in c.class_name().lower() for k in ('edit', 'text', 'combo'))
            if name and not dynamic:
                selector['title'] = name
            scope = 'main' if w.handle == attached['handle'] else 'popup'
            spec = {'scope': scope, 'selector': selector, 'action': 'click', 'write': 'text'}
            if scope == 'popup':
                spec['window'] = {'title': w.window_text(), 'class_name': w.class_name()}
            r = c.rectangle()
            items.append({'label': f'{w.window_text()[:35]} | {name[:65] or "(sin texto)"} | {c.class_name()} | {selector.get("auto_id", selector.get("control_id", ""))} | {r.left},{r.top}',
                          'spec': spec, 'text': name})
    return items
