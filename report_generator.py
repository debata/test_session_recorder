from jinja2 import Environment, PackageLoader
import os

class SessionReportGenerator:

    TEMPLATES_DIR = 'templates'
    TEMPLATE = 'report-template.html'

    def __init__(self, reports_dir):
        self.reports_dir = reports_dir
        if not os.path.exists(os.path.join(os.getcwd(), reports_dir)):
            os.makedirs(reports_dir)
        env = Environment(loader=PackageLoader('test_session', self.TEMPLATES_DIR))
        self.template = env.get_template(self.TEMPLATE)

    def generate_report(self, session_name='', session_mission='', test_areas=[], session_timebox='', session_duration='', session_log=[], bug_log=[], debrief=''):
        try:
            html_report = open(os.path.join(os.getcwd(), self.reports_dir, session_name + '.html'), 'w+')
            html_report.write((self.template.render(session_name=session_name, test_areas=test_areas, session_mission=session_mission, session_timebox=session_timebox, session_duration=session_duration, session_log=session_log, bugs=bug_log, debrief=debrief)))
        except:
            return False
        else:
            html_report.close()
            return True
