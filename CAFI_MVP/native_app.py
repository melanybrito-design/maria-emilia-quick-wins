"""Ventana Qt Widgets: sin HTML, navegador, servidor web ni consola operativa."""
import json
import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QFileDialog,
    QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPlainTextEdit, QProgressBar, QPushButton, QSpinBox, QVBoxLayout, QWidget, QScrollArea)

from config import ROOT, Rules
from excel_manager import validate
from journal import worker_lock, BusyError
from real_workflow import RealJournal, start_workflow
from windows_rpa import ROLES, REQUIRED, RpaError, empty_profile, inventory, list_windows, load_profile

PROFILE = ROOT / 'data' / 'perfil_cafi.json'
DATA = ROOT / 'data' / 'operacion'

STYLE = '''
QWidget { font-family: "Segoe UI", "Arial"; font-size: 14px; color: #26343c; }
QMainWindow, QDialog { background: #f7f5f6; }
QFrame#sidebar { background: #7e1233; border-radius: 0; }
QFrame#sidebar QLabel { color: white; background: transparent; }
QLabel#eyebrow { color: #8a1538; font-size: 12px; font-weight: 700; }
QLabel#heading { font-size: 28px; font-weight: 700; color: #192f39; }
QLabel#muted { color: #67737c; font-size: 13px; }
QFrame#card { background: white; border: 1px solid #e5dfe2; border-radius: 12px; }
QLabel#section { font-size: 17px; font-weight: 700; }
QLineEdit, QComboBox, QSpinBox { background: white; padding: 9px; border: 1px solid #d8cfd3; border-radius: 6px; min-height: 20px; }
QLineEdit:focus, QComboBox:focus { border: 2px solid #8a1538; }
QLineEdit:disabled { background: #f1eff0; color: #7e7478; }
QPushButton { background: white; color: #8a1538; padding: 10px 15px; border: 1px solid #d9c5cd; border-radius: 6px; font-weight: 600; }
QPushButton:hover { background: #f8ecf0; border-color: #8a1538; }
QPushButton#primary { background: #8a1538; color: white; border: 0; padding: 14px; }
QPushButton#primary:hover { background: #6f102d; }
QPushButton:disabled, QPushButton#primary:disabled { background: #eae5e7; color: #8c8085; border: 0; }
QCheckBox { spacing: 8px; padding: 4px 0; }
QProgressBar { border: 0; background: #eee7ea; height: 7px; border-radius: 3px; }
QProgressBar::chunk { background: #8a1538; border-radius: 3px; }
QPlainTextEdit { background: white; border: 1px solid #e5dfe2; border-radius: 6px; padding: 8px; }
'''


def label(text, name=None):
    item = QLabel(text)
    item.setWordWrap(True)
    if name:
        item.setObjectName(name)
    return item


def button(text, action, primary=False):
    item = QPushButton(text)
    if primary:
        item.setObjectName('primary')
    item.clicked.connect(action)
    item.setCursor(Qt.CursorShape.PointingHandCursor)
    return item


def card(title):
    frame = QFrame()
    frame.setObjectName('card')
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 16, 20, 18)
    layout.setSpacing(10)
    layout.addWidget(label(title, 'section'))
    return frame, layout


class Worker(QThread):
    progress = Signal(str)
    result = Signal(object)
    confirmation_requested = Signal(object)

    def __init__(self, arguments):
        super().__init__()
        self.arguments = arguments
        self.confirmation_event = threading.Event()
        self.confirmation_value = None

    def request_confirmation(self, row, result):
        self.confirmation_value = None
        self.confirmation_event.clear()
        self.confirmation_requested.emit({'row': row['row'], 'result': dict(result)})
        while not self.confirmation_event.wait(0.15):
            if self.arguments['stop_event'].is_set():
                return False
        return self.confirmation_value is True

    def answer_confirmation(self, accepted):
        self.confirmation_value = bool(accepted)
        self.confirmation_event.set()

    def run(self):
        # UI Automation usa COM por hilo. Nunca leer widgets desde el trabajador.
        initialized = False
        try:
            if os.name == 'nt':
                import pythoncom
                pythoncom.CoInitialize()
                initialized = True
            result = start_workflow(**self.arguments, progress=self.progress.emit,
                                    confirm_results=self.request_confirmation)
            self.result.emit(result)
        except (RpaError, ValueError) as exc:
            self.result.emit({'code': 3, 'message': str(exc)})
        except Exception:
            self.result.emit({'code': 3, 'message': 'No se pudo completar la operación. Revise CAFI y los resultados locales antes de retomar.'})
        finally:
            self.arguments.clear()
            if initialized:
                pythoncom.CoUninitialize()


class ProfileDialog(QDialog):
    """Configuración inicial por observación, sin enviar datos ni pulsar Guardar."""
    def __init__(self, attached, parent=None):
        super().__init__(parent)
        self.attached = attached
        self.profile = empty_profile()
        if PROFILE.exists():
            try:
                self.profile = json.loads(PROFILE.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                pass
        self.items = []
        self.setWindowTitle('Configurar CAFI · Controles de esta computadora')
        self.resize(880, 760)
        layout = QVBoxLayout(self)
        layout.addWidget(label('Conectar los campos de CAFI', 'heading'))
        layout.addWidget(label('Configuración inicial con apoyo técnico. Abre cada pantalla en CAFI y pulsa Leer controles. '
            'Asocia el campo o botón observado con su función. Esta ventana solo inspecciona; no crea trámites.', 'muted'))
        form = QFormLayout()
        self.backend = QComboBox()
        self.backend.addItems(['uia', 'win32'])
        self.backend.setCurrentText(self.profile['backend'])
        self.backend.currentTextChanged.connect(self.change_backend)
        form.addRow('Tecnología', self.backend)
        self.role = QComboBox()
        for key, value in ROLES.items():
            self.role.addItem(value, key)
        self.role.currentIndexChanged.connect(self.show_existing)
        form.addRow('Función del control', self.role)
        layout.addLayout(form)
        layout.addWidget(button('Leer controles de la pantalla abierta', self.inspect))
        self.candidates = QComboBox()
        self.candidates.setMinimumContentsLength(40)
        self.candidates.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.candidates.currentIndexChanged.connect(self.choose)
        layout.addWidget(self.candidates)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText('Aquí aparecerá el selector observado. No copie identificadores del RPA de Panacea.')
        self.editor.setMinimumHeight(135)
        layout.addWidget(self.editor)
        choices = QHBoxLayout()
        self.action = QComboBox()
        for text, value in [('Clic', 'click'), ('Doble clic', 'double_click'), ('Clic derecho', 'right_click'), ('Enter', 'enter')]:
            self.action.addItem(text, value)
        self.write = QComboBox()
        self.write.addItem('Campo de texto', 'text')
        self.write.addItem('Lista desplegable', 'select')
        choices.addWidget(self.action)
        choices.addWidget(self.write)
        choices.addWidget(button('Asignar a esta función', self.assign))
        layout.addLayout(choices)
        settings = QFormLayout()
        self.success = QLineEdit(self.profile['success_text'])
        settings.addRow('Confirmación exacta', self.success)
        self.process = QLineEdit(str(self.profile['process_value']))
        settings.addRow('Tipo de proceso', self.process)
        self.delay = QSpinBox()
        self.delay.setRange(10, 15)
        self.delay.setSuffix(' segundos')
        self.delay.setValue(int(float(self.profile.get('step_delay', 12))))
        settings.addRow('Espera entre acciones de CAFI', self.delay)
        layout.addLayout(settings)
        self.status = label('')
        layout.addWidget(self.status)
        layout.addWidget(label('Para campos cuyo contenido cambia (nombre, código, GPA, créditos), el selector no debe incluir su valor. '
            'Si CAFI no expone controles legibles en ninguno de los dos modos, conserva el inventario para ajustar el adaptador.', 'muted'))
        actions = QHBoxLayout()
        actions.addWidget(button('Guardar configuración', self.save, True))
        actions.addWidget(button('Cerrar', self.reject))
        layout.addLayout(actions)
        self.show_existing()
        self.update_status()

    def change_backend(self, backend):
        if backend != self.profile['backend']:
            self.profile = {**empty_profile(), 'backend': backend}
            self.candidates.clear()
            self.editor.clear()
            self.update_status()

    def show_existing(self):
        spec = self.profile['controls'].get(self.role.currentData())
        self.editor.setPlainText(json.dumps(spec, ensure_ascii=False, indent=2) if spec else '')
        if spec:
            self.action.setCurrentIndex(max(0, self.action.findData(spec.get('action', 'click'))))
            self.write.setCurrentIndex(max(0, self.write.findData(spec.get('write', 'text'))))

    def update_status(self):
        missing = REQUIRED - self.profile['controls'].keys()
        self.status.setText(f'{len(REQUIRED) - len(missing)} de {len(REQUIRED)} funciones de carga e impresión configuradas. '
                            'El acceso automático requiere además los 4 controles de Acceso.')

    def inspect(self):
        try:
            self.items = inventory(self.attached, self.backend.currentText())
            self.candidates.clear()
            self.candidates.addItem('Selecciona el control que corresponde…', None)
            for item in self.items:
                self.candidates.addItem(item['label'], item['spec'])
            # Inventario para soporte: no serializa texto ni valores de controles.
            output = ROOT / 'data' / 'inspeccion'
            output.mkdir(parents=True, exist_ok=True)
            structural = []
            for item in self.items:
                spec = json.loads(json.dumps(item['spec']))
                spec['selector'].pop('title', None)
                if spec.get('window'):
                    spec['window'].pop('title', None)
                structural.append(spec)
            (output / f'controles_{self.backend.currentText()}.json').write_text(
                json.dumps({'backend': self.backend.currentText(), 'controls': structural}, indent=2), encoding='utf-8')
        except Exception:
            QMessageBox.warning(self, 'Lectura de CAFI', 'No se pudieron leer los controles. Comprueba la ventana seleccionada y prueba el otro modo de tecnología.')

    def choose(self):
        original = self.candidates.currentData()
        if not original:
            return
        spec = json.loads(json.dumps(original))
        if self.role.currentData() in {'username', 'password', 'process', 'code', 'recipient', 'title', 'detail', 'priority',
                                      'print_destination', 'print_copies', 'transaction_id', 'gpa', 'credits'}:
            spec['selector'].pop('title', None)
        self.editor.setPlainText(json.dumps(spec, ensure_ascii=False, indent=2))

    def assign(self):
        try:
            spec = json.loads(self.editor.toPlainText())
            if not isinstance(spec, dict) or not spec.get('selector'):
                raise ValueError()
            spec['action'] = self.action.currentData()
            spec['write'] = self.write.currentData()
            self.profile['controls'][self.role.currentData()] = spec
            self.update_status()
        except ValueError:
            QMessageBox.warning(self, 'Control pendiente', 'Selecciona un control observado o corrige su configuración JSON.')

    def save(self):
        self.profile['success_text'] = self.success.text()
        self.profile['process_value'] = self.process.text()
        self.profile['step_delay'] = self.delay.value()
        PROFILE.parent.mkdir(parents=True, exist_ok=True)
        temporary = PROFILE.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.profile, indent=2, ensure_ascii=False), encoding='utf-8')
        temporary.replace(PROFILE)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.stop_event = threading.Event()
        self.workbook = None
        self.setWindowTitle('CAFI · Asistente de trámites UEES')
        self.setWindowIcon(QIcon(str(ROOT / 'assets' / 'cafi.ico')))
        available = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1060, available.width() - 40), min(880, available.height() - 50))
        container = QWidget()
        self.setCentralWidget(container)
        overall = QHBoxLayout(container)
        overall.setContentsMargins(0, 0, 0, 0)
        overall.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(240)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(26, 34, 26, 28)
        side.addWidget(label('UEES', 'heading'))
        side.addWidget(label('Universidad\nEspíritu Santo'))
        side.addSpacing(50)
        side.addWidget(label('Tu gestión,\npaso a paso.', 'heading'))
        side.addWidget(label('Asistente de trámites académicos'))
        side.addSpacing(32)
        for title, description in [('01  Conecta CAFI', 'Usa tu sesión o ingresa tus credenciales.'),
                                   ('02  Selecciona el Excel', 'Revisa los datos antes de iniciar.'),
                                   ('03  Inicia el proceso', 'Carga, impresión y resultados en una sola secuencia.')]:
            side.addWidget(label(title, 'section'))
            side.addWidget(label(description))
            side.addSpacing(20)
        side.addStretch()
        side.addWidget(label('QUICK WINS · GESTIÓN ADMINISTRATIVA'))
        side.addWidget(label('Ejecución local · v0.4.0'))
        overall.addWidget(sidebar)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        content = QVBoxLayout(body)
        content.setContentsMargins(30, 26, 30, 24)
        content.setSpacing(15)
        header = QHBoxLayout()
        heading = QVBoxLayout()
        heading.addWidget(label('ASISTENTE ADMINISTRATIVO', 'eyebrow'))
        heading.addWidget(label('Trámites CAFI', 'heading'))
        heading.addWidget(label('Del Excel al registro, con seguimiento en cada paso.', 'muted'))
        header.addLayout(heading)
        logo = QLabel()
        logo.setPixmap(QPixmap(str(ROOT / 'assets' / 'cafi-original.png')).scaled(
            105, 78, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        header.addWidget(logo)
        content.addLayout(header)
        access, layout = card('1. Conexión con CAFI')
        row = QHBoxLayout()
        self.windows = QComboBox()
        self.windows.addItem('Abre CAFI y busca su ventana…', None)
        self.windows.currentIndexChanged.connect(self.refresh_ready)
        row.addWidget(self.windows, 1)
        self.search = button('Buscar CAFI', self.refresh_windows)
        row.addWidget(self.search)
        layout.addLayout(row)
        fields = QHBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText('Usuario de CAFI')
        self.username.setAccessibleName('Usuario de CAFI')
        self.password = QLineEdit()
        self.password.setPlaceholderText('Contraseña')
        self.password.setAccessibleName('Contraseña de CAFI')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        fields.addWidget(self.username)
        fields.addWidget(self.password)
        layout.addLayout(fields)
        self.authenticated = QCheckBox('CAFI ya está abierto con la sesión iniciada')
        self.authenticated.toggled.connect(self.toggle_login)
        layout.addWidget(self.authenticated)
        layout.addWidget(label('Las credenciales se usan en esta ejecución y no se guardan en archivos.', 'muted'))
        content.addWidget(access)
        excel, layout = card('2. Archivo de trámites')
        row = QHBoxLayout()
        self.file_label = label('Ningún archivo seleccionado', 'muted')
        row.addWidget(self.file_label, 1)
        self.choose_button = button('Seleccionar Excel', self.choose_file)
        row.addWidget(self.choose_button)
        layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(label('Hoja'))
        self.sheet = QLineEdit('Hoja 1')
        row.addWidget(self.sheet, 1)
        row.addWidget(label('Dígitos del código'))
        self.code_length = QSpinBox()
        self.code_length.setRange(1, 30)
        self.code_length.setValue(10)
        row.addWidget(self.code_length)
        self.validate_button = button('Validar Excel', self.validate_file)
        row.addWidget(self.validate_button)
        layout.addLayout(row)
        self.excel_status = label('El archivo original se conserva. Los resultados se guardan en una copia.', 'muted')
        layout.addWidget(self.excel_status)
        content.addWidget(excel)
        progress, layout = card('3. Ejecución y resultados')
        self.status = label('Selecciona la ventana y el Excel para preparar el proceso.')
        layout.addWidget(self.status)
        self.progressbar = QProgressBar()
        self.progressbar.setRange(0, 1)
        self.progressbar.setValue(0)
        self.progressbar.setTextVisible(False)
        layout.addWidget(self.progressbar)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(85)
        self.log.setPlaceholderText('Aquí verás el avance de cada registro.')
        layout.addWidget(self.log)
        self.log.hide()
        row = QHBoxLayout()
        self.start_button = button('Iniciar proceso completo', self.start, True)
        row.addWidget(self.start_button, 1)
        self.stop_button = button('Detener', self.stop)
        self.stop_button.setEnabled(False)
        row.addWidget(self.stop_button)
        layout.addLayout(row)
        content.addWidget(progress)
        footer = QHBoxLayout()
        self.configure_button = button('Configurar CAFI', self.configure)
        footer.addWidget(self.configure_button)
        footer.addWidget(button('Resultados', self.results))
        footer.addWidget(button('Crear acceso directo', self.shortcut))
        content.addLayout(footer)
        self.setup_status = label('', 'muted')
        content.addWidget(self.setup_status)
        content.addStretch()
        scroll.setWidget(body)
        overall.addWidget(scroll, 1)
        self.refresh_ready()

    def toggle_login(self, checked):
        self.username.setDisabled(checked)
        self.password.setDisabled(checked)
        if checked:
            self.password.clear()
        self.refresh_ready()

    def refresh_ready(self):
        if not hasattr(self, 'start_button'):
            return
        configured = False
        try:
            load_profile(PROFILE, login=not self.authenticated.isChecked())
            configured = True
            message = 'Mapa cargado. La disponibilidad de los controles se comprueba en cada paso.'
        except RpaError:
            message = 'Primera instalación: usa «Configurar CAFI» para asociar los campos de esta computadora.'
        if os.name != 'nt':
            message = 'Esta ventana es nativa. Para conectar el robot, abre el paquete en la laptop Windows que tiene CAFI.'
        self.setup_status.setText(message)
        busy = self.worker is not None and self.worker.isRunning()
        self.start_button.setEnabled(os.name == 'nt' and configured and bool(self.workbook) and bool(self.windows.currentData()) and not busy)

    def refresh_windows(self):
        try:
            windows = list_windows()
            self.windows.clear()
            self.windows.addItem('Selecciona la ventana de CAFI…', None)
            for window in windows:
                self.windows.addItem(window['title'], window)
        except RpaError as exc:
            QMessageBox.information(self, 'Conexión local', str(exc))

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Seleccionar Excel de trámites', '', 'Libro de Excel (*.xlsx)')
        if path:
            self.workbook = Path(path)
            self.file_label.setText(self.workbook.name)
            self.validate_file()
            self.refresh_ready()

    def rules(self):
        return Rules(self.code_length.value(), self.sheet.text())

    def validate_file(self):
        if not self.workbook:
            QMessageBox.information(self, 'Excel', 'Selecciona primero tu archivo Excel.')
            return False
        try:
            report = validate(self.workbook.read_bytes(), self.rules())
            issues = [f'Fila {r["row"]}: ' + ' '.join(r['issues']) for r in report['rows'] if r['issues']]
            self.excel_status.setText(f'{len(report["rows"])} registros · {len(issues)} filas con incidencias · {report["blank_rows"]} filas vacías')
            if issues:
                detail = QDialog(self)
                detail.setWindowTitle('Incidencias del Excel')
                detail.resize(700, 430)
                layout = QVBoxLayout(detail)
                text = QPlainTextEdit('\n\n'.join(issues))
                text.setReadOnly(True)
                layout.addWidget(text)
                layout.addWidget(button('Cerrar', detail.accept))
                detail.exec()
            return not issues
        except (ValueError, OSError) as exc:
            message = str(exc) if isinstance(exc, ValueError) else 'No se pudo leer el archivo. Cierra Excel y vuelve a seleccionarlo.'
            self.excel_status.setText(message)
            return False

    def configure(self):
        selected = self.windows.currentData()
        if not selected:
            QMessageBox.information(self, 'Configurar CAFI', 'Busca las ventanas y selecciona CAFI primero.')
            return
        ProfileDialog(selected, self).exec()
        self.refresh_ready()

    def start(self):
        if self.worker and self.worker.isRunning():
            return
        if not self.validate_file():
            return
        if not self.authenticated.isChecked() and (not self.username.text().strip() or not self.password.text()):
            QMessageBox.information(self, 'Acceso CAFI', 'Completa usuario y contraseña, o indica que la sesión ya está iniciada.')
            return
        self.stop_event = threading.Event()
        self.worker = Worker(dict(attached=self.windows.currentData(), workbook=self.workbook, profile_path=PROFILE,
            data_root=DATA, username=self.username.text(), password=self.password.text(),
            authenticated=self.authenticated.isChecked(), rules=self.rules(), stop_event=self.stop_event))
        self.password.clear()
        self.worker.progress.connect(self.update_progress)
        self.worker.confirmation_requested.connect(self.confirm_results)
        self.worker.result.connect(self.finished)
        self.worker.finished.connect(self.release_worker)
        self.set_busy(True)
        self.progressbar.setRange(0, 0)
        self.log.clear()
        self.log.show()
        self.update_progress('Iniciando el lote. Mantén la sesión de Windows abierta y evita usar el teclado o mouse durante la carga.')
        self.worker.start()

    def confirm_results(self, payload):
        result = payload['result']
        message = (f"Se imprimió el trámite de la fila {payload['row']}.\n\n"
                   f"Código de trámite: {result['transaction_id']}\n"
                   f"GPA: {result['gpa']}\n"
                   f"Créditos aprobados: {result['credits']}\n\n"
                   'Confirma que los datos visibles en CAFI corresponden a esta fila. '
                   'Solo al confirmar se actualizará el Excel de resultados.')
        accepted = QMessageBox.question(self, 'Confirmar resultados impresos', message,
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        if self.worker:
            self.worker.answer_confirmation(accepted)

    def set_busy(self, busy):
        for widget in (self.windows, self.search, self.username, self.password, self.authenticated, self.sheet,
                       self.code_length, self.choose_button, self.validate_button, self.configure_button):
            widget.setDisabled(busy)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(busy)

    def update_progress(self, text):
        self.status.setText(text)
        self.log.appendPlainText(text)

    def stop(self):
        self.stop_event.set()
        self.stop_button.setEnabled(False)
        self.status.setText('Deteniendo en el siguiente punto de control. Un guardado ya enviado debe conciliarse en CAFI.')

    def finished(self, result):
        self.progressbar.setRange(0, 1)
        self.progressbar.setValue(1 if result['code'] == 0 else 0)
        self.update_progress(result['message'])
        if result.get('output'):
            self.log.appendPlainText('Archivo de salida: ' + str(Path(result['output']).name))

    def release_worker(self):
        self.worker.deleteLater()
        self.worker = None
        self.set_busy(False)
        self.toggle_login(self.authenticated.isChecked())
        self.refresh_ready()

    def results(self):
        try:
            journal = RealJournal(DATA)
            if not (self.worker and self.worker.isRunning()):
                with worker_lock(DATA):
                    journal.recover()
                    for run in journal.history():
                        journal.export(run['id'])
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA)))
        except (OSError, ValueError):
            QMessageBox.warning(self, 'Resultados', 'Cierra el Excel de resultados y vuelve a intentar. La bitácora se conserva.')

    def shortcut(self):
        if os.name != 'nt':
            QMessageBox.information(self, 'Acceso directo', 'Esta opción crea el icono en el escritorio de Windows.')
            return
        try:
            import win32com.client
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(Path(shell.SpecialFolders('Desktop')) / 'CAFI UEES.lnk'))
            shortcut.TargetPath = str(ROOT / 'CAFI.exe')
            shortcut.WorkingDirectory = str(ROOT)
            shortcut.IconLocation = str(ROOT / 'assets' / 'cafi.ico')
            shortcut.save()
            QMessageBox.information(self, 'Acceso directo', 'Se creó CAFI UEES en el escritorio. Conserva esta carpeta para que el icono funcione.')
        except Exception:
            QMessageBox.warning(self, 'Acceso directo', 'No se pudo crear el icono. Puedes abrir INICIAR_CAFI.bat desde esta carpeta.')

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.stop()
            event.ignore()
            return
        self.password.clear()
        event.accept()


def run_desktop():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName('CAFI UEES')
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    try:
        with worker_lock(ROOT / 'data' / 'native_app_lock'):
            window = MainWindow()
            window.show()
            return app.exec()
    except BusyError:
        QMessageBox.information(None, 'CAFI UEES', 'El asistente ya está abierto. Busca su ventana en la barra de tareas.')
        return 1


if __name__ == '__main__':
    raise SystemExit(run_desktop())
