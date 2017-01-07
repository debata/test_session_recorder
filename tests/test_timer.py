import datetime
import pytest
from modules.session_timer import DurationTimer

@pytest.fixture
def timer():
    timer = DurationTimer()
    return timer

def test_timer_no_change(timer):
    assert timer.get_duration() == datetime.timedelta(0), 'Unexpected timer value'

def test_timer_duration(timer):
    test_timer = timer #Force immediate instantiation for timing
    duration_in_seconds = 5
    wait(duration_in_seconds)
    assert test_timer.get_duration() == datetime.timedelta(seconds=duration_in_seconds), 'Timer duration was not ' + str(duration_in_seconds)

def test_timer_duration_with_pause(timer):
    test_timer = timer #Force immediate instantiation for timing
    test_timer.pause()
    wait(5)
    test_timer.unpause()
    assert timer.get_duration() == datetime.timedelta(0), 'Unexpected timer value'

def test_timer_duration_with_multiple_pauses(timer):
    test_timer = timer #Force immediate instantiation for timing
    test_timer.pause()
    wait(5)
    test_timer.unpause()
    wait(5)
    test_timer.pause()
    wait(5)
    test_timer.unpause()
    assert timer.get_duration() == datetime.timedelta(seconds=5), 'Unexpected timer value'

def test_timer_check_durations(timer):
    test_timer = timer #Force immediate instantiation for timing
    wait(2)
    assert timer.get_duration() == datetime.timedelta(seconds=2), 'Unexpected timer value'
    wait(5)
    assert timer.get_duration() == datetime.timedelta(seconds=7), 'Unexpected timer value'
    wait(5)
    assert timer.get_duration() == datetime.timedelta(seconds=12), 'Unexpected timer value'

def wait(duration_in_seconds):
    start_time = datetime.datetime.now().replace(microsecond=0)
    while not ((datetime.datetime.now().replace(microsecond=0) - start_time) == datetime.timedelta(seconds=duration_in_seconds)):
        pass #Wait 


