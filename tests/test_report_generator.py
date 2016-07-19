import pytest
import os
from modules.report_generator import SessionReportGenerator

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
    generator.generate_report(session_name=session_file_name, session_mission='Test Mession', test_areas=['Area 1', 'Area 2'], session_timebox='00:30:00', session_duration='00:20:00', session_log=['Entry 1'], bug_log=['Bug 1', 'Bug 2'], debrief='Test Debrief')
    assert os.path.isfile(os.path.join(str(tmp_dir), session_file_name + '.html')), 'Report file was not created'
