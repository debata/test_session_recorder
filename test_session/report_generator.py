from jinja2 import Environment, PackageLoader
import os


class SessionReportGenerator:

    TEMPLATES_DIR = 'templates'
    TEMPLATE = 'report-template.html'

    def __init__(self, reports_dir, package):
        self.reports_dir = reports_dir
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        env = Environment(loader=PackageLoader(package, self.TEMPLATES_DIR))
        self.template = env.get_template(self.TEMPLATE)

    def generate_report(self, session_name='', filename=None, **report_params):
        try:
            if filename:
                html_report = open(os.path.join(
                                   self.reports_dir, filename + '.html'),
                                   'w+')
            else:
                html_report = open(os.path.join(
                                   self.reports_dir, session_name + '.html'),
                                   'w+')
            html_report.write((self.template.render(
                session_name=session_name, **report_params)))
        except:
            return False
        else:
            html_report.close()
            return True
