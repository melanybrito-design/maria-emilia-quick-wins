import pytest

from session_controller import ConnectionPending, connection_status, start_attached_workflow

def test_workflow_requires_attached_window():
    status = connection_status()
    assert status['attached'] is False
    assert status['ready'] is False
    with pytest.raises(ConnectionPending, match='ventana'):
        start_attached_workflow(None, None)

def test_workflow_requires_observed_control_profile(tmp_path):
    assert connection_status(True)['attached'] is True
    with pytest.raises(ConnectionPending, match='mapa'):
        start_attached_workflow({'handle': 1234}, 'lote_sintetico.xlsx', profile_path=tmp_path/'absent.json')
