import time
import cmd
import os
import datetime
import shelve
import subprocess
from report_generator import SessionReportGenerator
from session import Session


class TestSessionRecorder(cmd.Cmd):
    # Constants
    # File System
    SESSION_DIR = 'sessions'
    REPORTS_DIR = 'reports'
    # Prompts
    DEFAULT_PROMPT = '>> '
    SESSION_PROMPT = 'SESSION >> '

    # Global Values
    prompt = DEFAULT_PROMPT
    session = None

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
                self.show_session(Session.get_session_data(session_name, self.SESSION_DIR))
                self.session = Session(session_name, self.SESSION_DIR, datetime.datetime.now().replace(microsecond=0))
                TestSessionRecorder.print_header ('Session Opened - ' + session_name)
                self.session_start_time = datetime.datetime.now().replace(microsecond=0)
                self.prompt = self.SESSION_PROMPT
            else:
                #Session does not exist so start a new one
                self.new_session(session_name)

    def complete_open(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def do_show(self, session_name):
        """show [session_name]
        Show contents of test session_name"""
        self.show_session(Session.get_session_data(session_name, self.SESSION_DIR))

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
                create_time = time.ctime(os.path.getmtime(os.path.join(self.SESSION_DIR, session)))
                print(' '*(self.columns-len(session)-len(create_time)) + create_time)
        else:
            print('There are no recorded sessions')

    def do_report(self, session_name):
        """report [session_name]
        Generate an HTML report for [session_name]"""
        if not session_name:
            print('Please enter a valid session name')
        elif self.check_for_session(session_name):
            generator = SessionReportGenerator(self.REPORTS_DIR, 'test_session_recorder')
            session_data = Session.get_session_data(session_name, self.SESSION_DIR)
            mission = session_data[Session.MISSION_KEY]
            timebox = session_data[Session.TIMEBOX_KEY]
            duration = session_data[Session.DURATION_KEY]
            log = session_data[Session.LOG_KEY]
            test_areas = session_data[Session.AREAS_KEY]
            debrief = session_data[Session.DEBRIEF_KEY]
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
        if self.session:
            timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            return self.session.process_session_cmd(timestamp, line)
        else:
            return line

    def default(self, line):
        if self.session:
            self.prompt = Session.SESSION_PROMPT
        else:
            print ('Please enter a valid command')
        if Session.SESSION_QUIT in line:
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

    def show_session(self, session_data):
            TestSessionRecorder.print_header('Test Session Contents')
            mission = session_data[Session.MISSION_KEY]
            timebox = session_data[Session.TIMEBOX_KEY]
            test_areas = session_data[Session.AREAS_KEY]
            debrief = session_data[Session.DEBRIEF_KEY]
            if mission is not None:
                print('Test Mission: ' + mission )
            if timebox is not None:
                print('Timebox: ' + timebox )
            if test_areas is not None:
                print('Test Areas:')
                for area in test_areas:
                    print('- ' + area)
            TesteselfessionRecorder.print_header('Test Session Log')
            log_entries = session_data[Session.LOG_KEY]
            for entry in log_entries:
                if entry['bug']:
                    print(entry['date'] + ' (BUG)' + entry['entry'])
                else:
                    print(entry['date'] + ' ' + entry['entry'])
            if debrief is not None:
                TestSessionRecorder.print_header('Debrief: ' + debrief)

    def new_session(self, session_name):
        TestSessionRecorder.print_header('Session Started: ' + session_name)
        self.prompt = Session.SESSION_PROMPT
        self.session = Session(session_name, self.SESSION_DIR, datetime.datetime.now().replace(microsecond=0))

    def quit_session(self):
        self.prompt = self.DEFAULT_PROMPT
        duration = self.session.get_duration()
        if duration is not None:
            duration += datetime.datetime.now().replace(microsecond=0) - self.session.get_session_start_time()
        else:
           duration = datetime.datetime.now().replace(microsecond=0) - self.session.get_session_start_time()
        self.session = self.session.quit(duration)
        print('Total Session Duration: ' + str(duration))
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

