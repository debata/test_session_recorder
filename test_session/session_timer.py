import datetime


class DurationTimer:
    def __init__(self, initial_duration=datetime.timedelta(seconds=0)):
        self.total_duration = 0
        self.initial_duration = initial_duration
        self.start_time = datetime.datetime.now().replace(microsecond=0)
        self.pause_intervals = []

    def pause(self):
        self.pause_start = datetime.datetime.now().replace(microsecond=0)
        return True

    def unpause(self):
        self.pause_interval = datetime.datetime.now().replace(microsecond=0)- self.pause_start
        self.pause_intervals.append(self.pause_interval)
        return False

    def get_duration(self):
        self.total_duration = datetime.datetime.now().replace(microsecond=0)- self.start_time
        for interval in self.pause_intervals:
            self.total_duration -= interval

        return self.total_duration + self.initial_duration
