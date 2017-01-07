import shelve
import os
import datetime
from .session_timer import DurationTimer


class Session:

    COMMANDS = {'bug': 'bug [bug_description] '
                '\n        Raise bug with a given description',
                'mission': 'mission [statement] '
                '\n        Set the Test Mission',
                'timebox': 'timebox [time_value] '
                '\n        Set the Test Timebox',
                'pause': 'pause \n        '
                'Pause the current session. Session resumes upon next entry',
                'duration': 'duration \n        '
                'Show the current session duration',
                'undo': 'undo \n        '
                'Undo the last test session entry',
                'areas': 'areas [area1, area2] '
                '\n        Set the list of Test Areas',
                'screenshot': 'screenshot \n        '
                'Take a screenshot of the current display [NOT IMPLEMENTED]',
                'help': 'help [command] '
                '\n        Display command and description'}
    CMD_KEY = 'cmd'
    TEXT_KEY = 'cmd_text'
    QUIT_CMD = 'quit'
    BUG_CMD = 'bug'
    MISSION_CMD = 'mission'
    TIMEBOX_CMD = 'timebox'
    UNDO_CMD = 'undo'
    AREAS_CMD = 'areas'
    SCREENSHOT_CMD = 'screenshot'
    SESSION_QUIT = '!SESSION_QUIT!'
    HELP_CMD = 'help'
    PAUSE_CMD = 'pause'
    DURATION_CMD = 'duration'
    PASS_THROUGH = 'passthrough '
    # File Keys
    SESSION_NAME_KEY = 'session_name'
    SESSION_KEY = 'session_data'
    LOG_KEY = 'session_log'
    BUG_KEY = 'bugs'
    MISSION_KEY = 'test_mission'
    TIMEBOX_KEY = 'session_timebox'
    DURATION_KEY = 'session_duration'
    AREAS_KEY = 'test_areas'
    DEBRIEF_KEY = 'session_debrief'
    SESSION_PROMPT = 'SESSION >> '

    def __init__(self, session_name, session_dir):
        self.session_dir = session_dir
        self.session_file = shelve.open(os.path.join(
            session_dir, session_name), writeback=True)
        self.paused = False
        self.pause_intervals = []
        # See if this is an existing session, if not initialize a skeleton
        try:
            self.duration = self.session_file[
                    self.SESSION_KEY][self.DURATION_KEY]
        except KeyError:
            self.session_file[self.SESSION_KEY] = {
                    self.LOG_KEY: [], self.TIMEBOX_KEY: None,
                    self.MISSION_KEY: None, self.DURATION_KEY: None,
                    self.AREAS_KEY: [], self.DEBRIEF_KEY: None}
            self.duration = datetime.timedelta(seconds=0)
        self.timer = DurationTimer(self.duration)

    @staticmethod
    def get_session_data(session_name, session_dir):
        read_file = shelve.open(os.path.join(session_dir, session_name))
        session_data = read_file[Session.SESSION_KEY]
        read_file.close()
        return session_data

    def get_duration(self):
        try:
            self.duration = self.session_file[
                    self.SESSION_KEY][self.DURATION_KEY]
            return self.duration
        except KeyError:
            return None

    def process_session_cmd(self, timestamp, line_data):
        # If session is in unpaused state,
        # immediately unpause and proceed with the command processor
        if self.paused:
            self.paused = self.timer.unpause()

        # Process session commands
        if line_data.rstrip() == 'quit':
            print('Would you like to record a debrief? (y/N)')
            confirmation = input()
            if confirmation.lower() in ['y', 'yes']:
                print('Debrief:', end=' ')
                debrief = input()
                self.session_file[self.SESSION_KEY][self.DEBRIEF_KEY] = debrief
            self.session_file[self.SESSION_KEY][
                    self.DURATION_KEY] = self.timer.get_duration()
            return {
                    self.CMD_KEY: self.PASS_THROUGH + self.SESSION_QUIT,
                    self.TEXT_KEY: ''}
        elif line_data.startswith(self.BUG_CMD):
            line_data = line_data[len(self.BUG_CMD):]
            self.session_file[self.SESSION_KEY][self.LOG_KEY].append(
                    {'date': timestamp, 'entry': line_data, 'bug': True})
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: 'Bug data captured'}
        elif line_data.startswith(self.TIMEBOX_CMD):
            line_data = line_data[len(self.TIMEBOX_CMD):]
            self.session_file[self.SESSION_KEY][self.TIMEBOX_KEY] = line_data
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY:
                    'Test time box saved'}
        elif line_data.startswith(self.MISSION_CMD):
            line_data = line_data[len(self.MISSION_CMD):]
            self.session_file[self.SESSION_KEY][self.MISSION_KEY] = line_data
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: 'Test mission saved'}
        elif line_data.rstrip() == self.SCREENSHOT_CMD:
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: '**Not Implemented yet**'}
        elif line_data.rstrip() == self.UNDO_CMD:
            self.session_file[self.SESSION_KEY][self.LOG_KEY].pop()
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: 'Last entry removed'}
        elif line_data.startswith(self.AREAS_CMD):
            areas = line_data[len(self.AREAS_CMD)+1:].split(sep=',')
            areas = [a.strip() for a in areas]
            areas = list(filter(None, areas))
            self.session_file[self.SESSION_KEY][self.AREAS_KEY] = areas
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: 'Test areas saved'}
        elif line_data.rstrip() == self.PAUSE_CMD:
            self.paused = self.timer.pause()
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: 'Session paused'}
        elif line_data.rstrip() == self.DURATION_CMD:
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: 'Duration: '+str(
                        self.timer.get_duration())}
        elif line_data.rstrip() == self.HELP_CMD:
            commands = list(self.COMMANDS.keys())
            help_text = 'Available session commands'
            for cmd in commands:
                help_text += cmd + '  \n'
            help_text = help_text.rstrip()
            return {
                    self.CMD_KEY: self.PASS_THROUGH,
                    self.TEXT_KEY: help_text}
        elif line_data.startswith(self.HELP_CMD):
            command = line_data[len(self.AREAS_CMD):]
            try:
                return {
                        self.CMD_KEY: self.PASS_THROUGH,
                        self.TEXT_KEY: self.COMMANDS[command]}
            except KeyError:
                return {
                        self.CMD_KEY: self.PASS_THROUGH,
                        self.TEXT_KEY: command + ' command does not exist'}
        else:
            # Write to session fil
            self.session_file[
                    self.SESSION_KEY][self.LOG_KEY].append(
                            {'date': timestamp,
                             'entry': ' '+line_data, 'bug': False})
            return {
                    self.CMD_KEY: self.PASS_THROUGH, self.TEXT_KEY: ''}
