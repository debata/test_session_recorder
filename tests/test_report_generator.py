import pytest
import os
from modules.report_generator import SessionReportGenerator
from modules.session import Session

@pytest.fixture(scope='session')
def generator(tmpdir_factory):
    """Create the report generator object and pass in a temporary directory for testing"""
    global tmp_dir
    tmp_dir = tmpdir_factory.mktemp('test')
    generator = SessionReportGenerator(str(tmp_dir), 'test_session_recorder')
    return generator

def test_generate_report(generator):
    """Test to generate an empty report with just the test session name"""
    session_file_name = 'test_report'
    generator.generate_report(session_name=session_file_name)
    assert os.path.isfile(os.path.join(str(tmp_dir), session_file_name + '.html')), 'Report file was not created'

def test_invalid_report_name(generator):
    """Test to validate that a report cannot be generated with the session name contains invalid characters"""
    assert not generator.generate_report(session_name='/////'), 'Generator should have returned false'

def test_generate_all_values_report(generator):
    """Test to generate a report with all report values set"""
    session_file_name = 'All Value Report'
    report_data = {Session.SESSION_NAME_KEY:session_file_name, Session.MISSION_KEY:'Test Mession', Session.AREAS_KEY:['Area 1', 'Area 2'], Session.TIMEBOX_KEY:'00:30:00', Session.DURATION_KEY:'00:20:00', Session.LOG_KEY:['Entry 1'], Session.BUG_KEY:['Bug 1', 'Bug 2'], Session.DEBRIEF_KEY:'Test Debrief'}
    generator.generate_report(**report_data)
    assert os.path.isfile(os.path.join(str(tmp_dir), session_file_name + '.html')), 'Report file was not created'

def test_generate_report_new_filename(generator):
    """Test to generate a report with all report values set"""
    session_filename = 'alternate_file'
    session_name = 'Session1'
    report_data = {Session.SESSION_NAME_KEY:session_name, Session.MISSION_KEY:'Test Mession', Session.AREAS_KEY:['Area 1', 'Area 2'], Session.TIMEBOX_KEY:'00:30:00', Session.DURATION_KEY:'00:20:00', Session.LOG_KEY:['Entry 1'], Session.BUG_KEY:['Bug 1', 'Bug 2'], Session.DEBRIEF_KEY:'Test Debrief'}
    generator.generate_report(filename=session_filename, **report_data)
    assert os.path.isfile(os.path.join(str(tmp_dir), session_filename + '.html')), 'Report file was not created'

