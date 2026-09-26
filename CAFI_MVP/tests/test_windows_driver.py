"""Contratos del controlador con controles falsos; no afirman compatibilidad CAFI."""
import threading
from types import SimpleNamespace

import pytest

from windows_rpa import REQUIRED, RpaError, StopRequested, WindowsDriver, empty_profile, matches, validate_profile


class Control:
    def __init__(self, value='', name='Campo', automation_id='observed-id'):
        self.value, self.name = value, name
        self.element_info = SimpleNamespace(automation_id=automation_id, control_id=1, control_type='Edit')
        self.sent = []

    def class_name(self):
        return 'TestControl'

    def window_text(self):
        return self.name

    def set_edit_text(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_focus(self):
        pass

    def type_keys(self, text):
        self.sent.append(text)


def fake_driver(controls):
    driver = object.__new__(WindowsDriver)
    driver.profile = empty_profile()
    driver.profile['timeout'] = 0
    driver.profile['controls'] = {role: {} for role in controls}
    driver.stop = threading.Event()
    driver.find = lambda role, timeout=None: controls[role]
    driver.focus = lambda control: None
    driver.settle = lambda: None
    return driver


def test_literal_excel_text_never_becomes_keyboard_commands():
    control = Control()
    driver = fake_driver({'detail': control})
    value = 'Revisión académica: {ENTER} + % ^ ~\nTítulo con acentos.'
    driver.write('detail', value)
    assert control.value == value
    assert control.sent == []


def test_only_explicit_enter_is_sent_after_code_readback():
    control = Control()
    driver = fake_driver({'code': control})
    driver.write('code', '0000000017', enter=True)
    assert control.value == '0000000017'
    assert control.sent == ['{ENTER}']


def test_password_is_not_read_back_or_copied():
    control = Control()
    control.get_value = lambda: (_ for _ in ()).throw(AssertionError('password readback'))
    driver = fake_driver({'password': control})
    driver.write('password', 'Private{ENTER}%+Secret', secret=True)
    assert control.value == 'Private{ENTER}%+Secret'
    assert not control.sent


def test_write_failure_does_not_expose_secret():
    control = Control()
    def fail(value):
        raise RuntimeError(value)
    control.set_edit_text = fail
    driver = fake_driver({'password': control})
    with pytest.raises(RpaError) as captured:
        driver.write('password', 'PRIVATE-PASSWORD', secret=True)
    assert 'PRIVATE-PASSWORD' not in str(captured.value)


def test_readback_mismatch_is_error():
    driver = fake_driver({'code': Control('0000000018')})
    with pytest.raises(RpaError, match='no coincide'):
        driver.expect('code', '0000000017')


def test_matching_is_exact_and_does_not_use_best_match():
    control = Control(name='Nombre de prueba', automation_id='42')
    assert matches(control, {'class_name': 'TestControl', 'auto_id': '42'})
    assert not matches(control, {'auto_id': '4'})
    assert not matches(control, {'title': 'Nombre'})


def test_cancellation_checked_before_control_lookup():
    driver = object.__new__(WindowsDriver)
    driver.stop = threading.Event()
    driver.stop.set()
    driver.check_identity = lambda: (_ for _ in ()).throw(AssertionError('identity lookup'))
    with pytest.raises(StopRequested):
        driver.check_stop()


def profile():
    config = empty_profile()
    config['controls'] = {role: {'scope': 'main', 'selector': {'auto_id': 'TEST-' + role}}
                          for role in REQUIRED}
    return config


def test_no_login_fields_needed_for_authenticated_session():
    validate_profile(profile())
    with pytest.raises(RpaError, match='Acceso'):
        validate_profile(profile(), login=True)


@pytest.mark.parametrize('selector', [{}, {'best_match': 'Guardar'}, {'found_index': 0}, {'script': 'arbitrary code'}])
def test_empty_fuzzy_or_executable_selector_is_rejected(selector):
    config = profile()
    config['controls']['save']['selector'] = selector
    with pytest.raises(RpaError, match='Selector'):
        validate_profile(config)


def test_foreign_navigation_is_rejected():
    config = profile()
    config['navigation'] = ['execute_shell']
    with pytest.raises(RpaError, match='navegación'):
        validate_profile(config)


def test_empty_or_nonnumeric_transaction_cannot_be_reported_complete():
    driver = fake_driver({'transaction_id': Control(''), 'gpa': Control('8.1'), 'credits': Control('90')})
    with pytest.raises(RpaError, match='resultados'):
        driver.results()


def test_save_does_not_retry_on_missing_success():
    driver = fake_driver({})
    clicks = []
    driver.click = clicks.append
    def absent(role, expected):
        raise RpaError('No se encontró la confirmación')
    driver.expect = absent
    with pytest.raises(RpaError):
        driver.save()
    assert clicks == ['save']
