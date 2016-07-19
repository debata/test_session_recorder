import pytest
import test
import datetime
import os
from session import Session

@pytest.fixture
def session(tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp('test')
    session = Session('TestSession', str(tmp_dir), datetime.datetime.now().replace(microsecond=0))
    return session

def test_no_duration(session):
    assert session.get_duration() is None, 'Unexpected duration'

def test_bug_cmd(session):
    assert session.process_session_cmd('Any time', Session.BUG_CMD) == Session.PASS_THROUGH, 'Unexpected pass through value'
