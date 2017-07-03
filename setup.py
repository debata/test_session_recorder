import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(name='test_session',
      version='0.1',
      description='Interactive CLI test session recorder',
      url='https://github.com/debata/test_session_recorder',
      author='Daryl Ebata',
      author_email='daryl.ebata@gmail.com',
      keywords='agile software testing exploratory',
      license='Apache',
      packages=['test_session'],
      zip_safe=False,
      python_requires='>=3',
      install_requires=['datetime', 'jinja2'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'testrecorder = test_session.start:main'
          ]
      })
