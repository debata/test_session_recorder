import time
import cmd
import os
import datetime
import shelve
import subprocess
from report_generator import SessionReportGenerator

SCREEN_WIDTH = 35

class TestSessionRecorder(cmd.Cmd):
    # Constants
    # Session Commands
    COMMANDS = {'bug':'bug [bug_description] \n        Raise bug with a given description',
        'mission':'mission [statement] \n        Set the Test Mission',
        'timebox':'timebox [time_value] \n        Set the Test Timebox',
        'undo': 'undo \n        Undo the last test session entry',
        'areas': 'areas [area1, area2] \n        Set the list of Test Areas',
        'screenshot': 'screenshot \n        Take a screenshot of the current display [NOT IMPLEMENTED]',
        'help': 'help [command] \n        Display command and description'}
    PASS_THROUGH = 'passthrough '
    BUG_CMD = 'bug'
    MISSION_CMD = 'mission'
    TIMEBOX_CMD = 'timebox'
    UNDO_CMD = 'undo'
    AREAS_CMD =  'areas'
    SCREENSHOT_CMD = 'screenshot'
    SESSION_QUIT = '!SESSION_QUIT!'
    HELP_CMD = 'help'
    # File Keys
    SESSION_KEY = 'session_data'
    LOG_KEY = 'test_log'
    MISSION_KEY = 'test_mission'
    TIMEBOX_KEY = 'timebox'
    DURATION_KEY = 'test_duration'
    AREAS_KEY = 'test_areas'
    DEBRIEF_KEY = 'defrief'
    # File System
    SESSION_DIR = 'sessions'
    REPORTS_DIR = 'reports'
    # Prompts
    DEFAULT_PROMPT = '>> '
    SESSION_PROMPT = 'SESSION >> '

    # Global Values
    prompt = DEFAULT_PROMPT
    mode = 'init'
    session_start_time = None
    try:
        FNULL = open(os.devnull, 'w')
        rows, columns = subprocess.check_output(['stty', 'size'], strerr=FNULL).decode('utf-8').split()
    except:
        rows = 0
        columns = 80

    def preloop(self):
        if not os.path.exists(os.path.join(os.getcwd(),self.SESSION_DIR)):
           os.makedirs(self.SESSION_DIR)

    def do_new(self, session_name):
        """new [session_name]
        Create a new test session as session_name"""
        if not session_name:
            print('Test session must have a name or title')
        elif self.check_for_session(session_name):
            print('This test session already exists. Please try again with a different title')
        else:
            self.new_session(session_name)

    def do_open(self, session_name):
        """open [session_name]
        Open test session_name or start a new session if session_name does not exist"""
        if not session_name:
            print('Please specify a test session to open')
        else:
            if self.check_for_session(session_name):
                self.show_session(session_name)
                global session_file
                session_file = shelve.open(os.path.join(self.SESSION_DIR, session_name), writeback=True)
                TestSessionRecorder.print_header ('Session Opened - ' + session_name)
                self.session_start_time = datetime.datetime.now().replace(microsecond=0)
                self.mode = 'in_session'
                self.prompt = self.SESSION_PROMPT
            else:
                #Session does not exist so start a new one
                self.new_session(session_name)

    def complete_open(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def do_show(self, session_name):
        """show [session_name]
        Show contents of test session_name"""
        self.show_session(session_name)

    def complete_show(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def do_list(self, line):
        """list
        List all test sessions"""
        all_sessions = os.listdir(self.SESSION_DIR)
        if len(all_sessions) > 0:
            TestSessionRecorder.print_header('Test Sessions')
            for session in all_sessions:
                print(session, end='')
                print(' '*(SCREEN_WIDTH-len(session)) + time.ctime(os.path.getmtime(os.path.join(self.SESSION_DIR, session))))
        else:
            print('There are no recorded sessions')

    def do_report(self, session_name):
        """report [session_name]
        Generate an HTML report for [session_name]"""
        if not session_name:
            print('Please enter a valid session name')
        elif self.check_for_session(session_name):
            generator = SessionReportGenerator(self.REPORTS_DIR)
            read_session = shelve.open(os.path.join(self.SESSION_DIR, session_name))
            mission = read_session[self.SESSION_KEY][self.MISSION_KEY]
            timebox = read_session[self.SESSION_KEY][self.TIMEBOX_KEY]
            duration = read_session[self.SESSION_KEY][self.DURATION_KEY]
            log = read_session[self.SESSION_KEY][self.LOG_KEY]
            test_areas = read_session[self.SESSION_KEY][self.AREAS_KEY]
            debrief = read_session[self.SESSION_KEY][self.DEBRIEF_KEY]
            test_log = []
            bug_log = []
            for entry in log:
                if entry['bug']:
                    bug_log.append(entry['date'] + ' ' + entry['entry'])
                else:
                    test_log.append(entry['date'] + ' ' + entry['entry'])
            if generator.generate_report(session_name, mission, test_areas, timebox, duration, test_log, bug_log, debrief):
                print('Report sucessfully generated')
            else:
                print('Report failed to generate')
        else:
            print('There is no test session with that name')

    def complete_report(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def precmd(self, line):
        if self.mode == 'in_session':
            timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            if line.rstrip() == 'quit':
                print('Would you like to record a debrief? (y/N)')
                confirmation = input()
                if confirmation.lower() in ['y', 'yes']:
                    print('Debrief:', end=' ')
                    debrief = input()
                    session_file[self.SESSION_KEY][self.DEBRIEF_KEY] = debrief
                return self.PASS_THROUGH + self.SESSION_QUIT
            elif line.startswith(self.BUG_CMD):
                line_data = line[len(self.BUG_CMD):]
                session_file[self.SESSION_KEY][self.LOG_KEY].append({'date':timestamp, 'entry':line_data, 'bug':True})
                print('Bug data captured')
                return self.PASS_THROUGH
            elif line.startswith(self.TIMEBOX_CMD):
                line_data = line[len(self.TIMEBOX_CMD):]
                session_file[self.SESSION_KEY][self.TIMEBOX_KEY] = line_data
                print('Test time box saved')
                return self.PASS_THROUGH
            elif line.startswith(self.MISSION_CMD):
                line_data = line[len(self.MISSION_CMD):]
                session_file[self.SESSION_KEY][self.MISSION_KEY] = line_data
                print('Test mission saved')
                return self.PASS_THROUGH
            elif line.rstrip() == self.SCREENSHOT_CMD:
               pass
            elif line.rstrip() == self.UNDO_CMD:
                session_file[self.SESSION_KEY][self.LOG_KEY].pop()
                print('Last entry removed')
                return self.PASS_THROUGH
            elif line.startswith(self.AREAS_CMD):
                areas = line[len(self.AREAS_CMD)+1:].split(sep=',')
                areas = [a.strip() for a in areas]
                areas = list(filter(None, areas))
                session_file[self.SESSION_KEY][self.AREAS_KEY] = areas
                print('Test areas saved')
                return self.PASS_THROUGH
            elif line.rstrip() == self.HELP_CMD:
                commands = list(self.COMMANDS.keys())
                for cmd in commands:
                    print(cmd , end='  ')
                print('')
                return self.PASS_THROUGH
            elif line.startswith(self.HELP_CMD):
                command = line[len(self.AREAS_CMD):]
                try:
                    print(self.COMMANDS[command])
                except KeyError:
                    print(command + ' command does not exist')
                return self.PASS_THROUGH
            else:
                # Write to session file
                session_file[self.SESSION_KEY][self.LOG_KEY].append({'date':timestamp, 'entry':' '+line, 'bug':False})
                return self.PASS_THROUGH
        else:
            return line

    def default(self, line):
        if self.mode == 'init':
            print ('Please enter a valid command')
        if self.SESSION_QUIT in line:
            self.quit_session()

    def do_delete(self, session_name):
        """delete [session_name]
        Permanently delete test session_name"""
        if not session_name:
            print('Please enter a valid session name')
        elif self.check_for_session(session_name):
            print('Are you sure you want to delete {} ? (y/N)'.format(session_name))
            confirmation = input()
            self.delete_session( session_name, confirmation)
        else:
            print('There is no test session with that name')

    def delete_session(self, session_name, choice):
            if choice.lower() in ['y', 'yes']:
                os.remove(os.path.join(self.SESSION_DIR, session_name))
                print(session_name + ' successfully deleted')

    def complete_delete(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def do_quit(self, line):
        """quit
        Quit the application or current test session"""
        return True

    def check_for_session(self, session_name):
        all_sessions = os.listdir(self.SESSION_DIR)
        return session_name in all_sessions

    def show_session(self, session_name):
        if self.check_for_session(session_name):
            TestSessionRecorder.print_header('Test Session Contents')
            read_session = shelve.open(os.path.join(self.SESSION_DIR, session_name))
            mission = read_session[self.SESSION_KEY][self.MISSION_KEY]
            timebox = read_session[self.SESSION_KEY][self.TIMEBOX_KEY]
            test_areas = read_session[self.SESSION_KEY][self.AREAS_KEY]
            debrief = read_session[self.SESSION_KEY][self.DEBRIEF_KEY]
            if mission is not None:
                print('Test Mission: ' + mission )
            if timebox is not None:
                print('Timebox: ' + timebox )
            if test_areas is not None:
                print('Test Areas:')
                for area in test_areas:
                    print('- ' + area)
            TestSessionRecorder.print_header('Test Session Log')
            log_entries = read_session[self.SESSION_KEY][self.LOG_KEY]
            for entry in log_entries:
                if entry['bug']:
                    print(entry['date'] + ' (BUG)' + entry['entry'])
                else:
                    print(entry['date'] + ' ' + entry['entry'])
            if debrief is not None:
                TestSessionRecorder.print_header('Debrief: ' + debrief)
            read_session.close()
        else:
            print('Test Session not found')

    def new_session(self, session_name):
        TestSessionRecorder.print_header('Session Started: ' + session_name)
        self.session_start_time = datetime.datetime.now().replace(microsecond=0)
        self.mode = 'in_session'
        self.prompt = self.SESSION_PROMPT
        global session_file
        session_file = shelve.open(os.path.join(self.SESSION_DIR, session_name), writeback=True)
        session_file[self.SESSION_KEY] = {self.LOG_KEY:[], self.TIMEBOX_KEY:None, self.MISSION_KEY:None, self.DURATION_KEY:None, self.AREAS_KEY:[], self.DEBRIEF_KEY:None}

    def quit_session(self):
        self.prompt = self.DEFAULT_PROMPT
        self.mode = 'init'
        duration = session_file[self.SESSION_KEY][self.DURATION_KEY]
        if duration is not None:
            duration += datetime.datetime.now().replace(microsecond=0) - self.session_start_time
        else:
           duration = datetime.datetime.now().replace(microsecond=0) - self.session_start_time
        session_file[self.SESSION_KEY][self.DURATION_KEY] = duration
        print('Total Session Duration: ' + str(duration))
        session_file.close()
        print('Session saved.')

    def autocomplete_sessions(self, text, line, begidx, endidx):
        all_sessions = os.listdir(self.SESSION_DIR)
        if not text:
            completions = all_sessions[:]
        else:
            completions = [f for f in all_sessions if f.startswith(text)]
        return completions

    @classmethod
    def print_header(cls, header_text):
        print('='*int(TestSessionRecorder.columns))
        print(header_text)
        print('='*int(TestSessionRecorder.columns))

if __name__ == '__main__':
    TestSessionRecorder().cmdloop(TestSessionRecorder.print_header('Test Session Recorder'))

