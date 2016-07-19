import pytest
import test
import datetime
import os
from modules.session import Session

@pytest.fixture
def session(tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp('test')
    session = Session('TestSession', str(tmp_dir), datetime.datetime.now().replace(microsecond=0))
    return session

@pytest.fixture
def timestamp():
    timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    return timestamp

def test_no_duration(session):
    assert session.get_duration() is None, 'Unexpected duration'

def test_bug_cmd(session, timestamp):
    result = session.process_session_cmd(timestamp, Session.BUG_CMD)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == 'Bug data captured', 'Unexpected command message'
def test_timebox_cmd(session, timestamp):
    result = session.process_session_cmd(timestamp, Session.TIMEBOX_CMD)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == 'Test time box saved', 'Unexpected command message'
def test_mission_cmd(session, timestamp):
    result = session.process_session_cmd(timestamp, Session.MISSION_CMD)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == 'Test mission saved', 'Unexpected command message'
def test_areas_cmd(session, timestamp):
    result = session.process_session_cmd(timestamp, Session.AREAS_CMD)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == 'Test areas saved', 'Unexpected command message'
def test_undo_cmd(session, timestamp):
    session.process_session_cmd(timestamp, 'Entry')
    result = session.process_session_cmd(timestamp, Session.UNDO_CMD)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == 'Last entry removed', 'Unexpected command message'
def test_invalid_help_cmd(session,timestamp):
    bad_cmd = 'invalid'
    result = session.process_session_cmd(timestamp, Session.HELP_CMD + ' ' + bad_cmd)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == bad_cmd + ' command does not exist','Unexpected help command message'
def test_valid_help_cmd(session, timestamp):
    result = session.process_session_cmd(timestamp, Session.HELP_CMD + ' ' + Session.MISSION_CMD)
    assert result[Session.CMD_KEY] == Session.PASS_THROUGH, 'Unexpected command value'
    assert result[Session.TEXT_KEY] == 'mission [statement] \n        Set the Test Mission','Unexpected help command message'
