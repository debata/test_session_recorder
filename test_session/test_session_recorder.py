import time
import cmd
import os
import datetime
import subprocess
from .report_generator import SessionReportGenerator
from .print_colour import Printer
from .session import Session


class TestSessionRecorder(cmd.Cmd):
    # Constants
    # File System
    SESSION_DIR = os.path.expanduser("~") + '/sessions'
    REPORTS_DIR = os.path.expanduser("~") + '/reports'
    # Prompts
    DEFAULT_PROMPT = '>> '

    # Global Values
    prompt = DEFAULT_PROMPT
    intro = 'Test Session Recorder is simply utility that allows a'
    'tester to capture and log test session data easily in an '
    'interactive command line format. Sessions can be viewed '
    'later or outputted to an HTML report'
    session = None

    try:
        rows, columns = subprocess.check_output(
                ['stty', 'size']).decode('utf-8').split()
        columns = int(columns)
    except:
        rows = 0
        columns = 80

    def preloop(self):
        if not os.path.exists(os.path.join(self.SESSION_DIR)):
            os.makedirs(self.SESSION_DIR)

    def do_new(self, session_name):
        """new [session_name]
        Create a new test session as session_name"""
        if not session_name:
            print('Test session must have a name or title')
        elif self.check_for_session(session_name):
            print('This test session already exists. Please try again with a'
                  ' different title')
        else:
            self.new_session(session_name)

    def do_open(self, session_name):
        """open [session_name]
        Open test session_name or start a new session if
         session_name does not exist"""
        if not session_name:
            print('Please specify a test session to open')
        else:
            if self.check_for_session(session_name):
                TestSessionRecorder.print_header(
                        'Session Opened - ' + session_name)
                self.show_session(
                        Session.get_session_data(
                            session_name, self.SESSION_DIR))
                self.session = Session(session_name, self.SESSION_DIR)
                self.prompt = Session.SESSION_PROMPT
            else:
                # Session does not exist so start a new one
                self.new_session(session_name)

    def complete_open(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def do_show(self, session_name):
        """show [session_name]
        Show contents of test session_name"""
        self.show_session(Session.get_session_data(
            session_name, self.SESSION_DIR))

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
                create_time = time.ctime(os.path.getmtime(
                    os.path.join(self.SESSION_DIR, session)))
                print(' '*(self.columns-len(session)-len(create_time))
                      + create_time)
        else:
            print('There are no recorded sessions')

    def do_report(self, report_args):
        """report [report_args]
        Generate an HTML report for [session_name] -f [optional_filename]"""
        args = report_args.split('-f')
        if len(args) == 0:
            print('Please enter a valid session name')
        elif len(args) >= 1:
            session_name = args[0].strip()
            if self.check_for_session(session_name):
                generator = SessionReportGenerator(self.REPORTS_DIR,
                                                   'test_session')
                session_data = Session.get_session_data(
                        session_name, self.SESSION_DIR)
                log = session_data[Session.LOG_KEY]
                test_log = []
                bug_log = []
                for entry in log:
                    if entry['bug']:
                        bug_log.append(entry['date'] + ' ' + entry['entry'])
                    else:
                        test_log.append(entry['date'] + ' ' + entry['entry'])
                session_data[Session.BUG_KEY] = bug_log
                session_data[Session.LOG_KEY] = test_log
                if len(args) == 2:
                    filename = args[1].strip()
                    result = generator.generate_report(
                           session_name, filename, **session_data)
                else:
                    result = generator.generate_report(
                                session_name, **session_data)
                if result:
                    print('Report sucessfully generated')
                else:
                    print('Report failed to generate')
            else:
                print('Session name not found')
        else:
            print('Invalid report arguments')

    def complete_report(self, text, line, begidx, endidx):
        return self.autocomplete_sessions(text, line, begidx, endidx)

    def precmd(self, line):
        if self.session:
            timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            result = self.session.process_session_cmd(timestamp, line)
            console_text = result[Session.TEXT_KEY]
            if console_text:
                print(console_text)
            return result[Session.CMD_KEY]
        else:
            return line

    def default(self, line):
        if self.session:
            self.prompt = Session.SESSION_PROMPT
            if Session.SESSION_QUIT in line:
                self.quit_session()
        else:
            print('Please enter a valid command')

    def do_delete(self, session_name):
        """delete [session_name]
        Permanently delete test session_name"""
        if not session_name:
            print('Please enter a valid session name')
        elif self.check_for_session(session_name):
            print('Are you sure you want to delete {} ? (y/N)'.format(
                session_name))
            confirmation = input()
            self.delete_session(session_name, confirmation)
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
            TestSessionRecorder.print_header('Test Session Contents', True)
            mission = session_data[Session.MISSION_KEY]
            timebox = session_data[Session.TIMEBOX_KEY]
            test_areas = session_data[Session.AREAS_KEY]
            debrief = session_data[Session.DEBRIEF_KEY]
            if mission is not None:
                Printer.print('Test Mission: ', end='')
                print(mission)
            if timebox is not None:
                Printer.print('Timebox: ', end='')
                print(timebox)
            if len(test_areas) != 0:
                Printer.print('Test Areas:')
                for area in test_areas:
                    print('- ' + area)
            TestSessionRecorder.print_bar()
            TestSessionRecorder.print_header('Test Session Log', True)
            log_entries = session_data[Session.LOG_KEY]
            if len(log_entries) > 0:
                for entry in log_entries:
                    if entry['bug']:
                        Printer.print(
                                entry['date'] + ' (BUG)' + entry['entry'],
                                Printer.WARNING)
                    else:
                        print(entry['date'] + ' ' + entry['entry'])
                TestSessionRecorder.print_bar()
            if debrief is not None:
                Printer.print('Debrief: ', end='')
                print(debrief)
            Printer.print('Duration: ', end='')
            print(session_data[Session.DURATION_KEY])

    def new_session(self, session_name):
        print('Session Started: ' + session_name)
        TestSessionRecorder.print_bar()
        self.prompt = Session.SESSION_PROMPT
        self.session = Session(session_name, self.SESSION_DIR)

    def quit_session(self):
        self.prompt = self.DEFAULT_PROMPT
        duration = self.session.get_duration()
        print('Session Duration: ' + str(duration))
        print('Session saved.')
        self.session = None

    def autocomplete_sessions(self, text, line, begidx, endidx):
        all_sessions = os.listdir(self.SESSION_DIR)
        if not text:
            completions = all_sessions[:]
        else:
            completions = [f for f in all_sessions if f.startswith(text)]
        return completions

    @classmethod
    def print_header(cls, header_text, center=False):
        if center:
            Printer.print(' '*(int(TestSessionRecorder.columns/2)-int(
                (len(header_text)/2))) + header_text, Printer.BLUE)
        else:
            Printer.print(header_text, Printer.BLUE)
        TestSessionRecorder.print_bar()

    @classmethod
    def print_bar(cls):
        print('='*TestSessionRecorder.columns)

if __name__ == '__main__':
    TestSessionRecorder().cmdloop(
            TestSessionRecorder.print_header('Test Session Recorder', True))
