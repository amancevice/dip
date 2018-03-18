import textwrap
from setuptools import setup


setup(name='dip',
      version='2.1.1',
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['dip'],
      url='http://www.smallweirdnumber.com',
      description='Install CLIs using docker-compose',
      long_description=textwrap.dedent(
          '''See GitHub_ for documentation.
          .. _GitHub: https://github.com/amancevice/dip'''),
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Utilities',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python'],
      install_requires=['click >= 6.7.0',
                        'colored >= 1.3.4',
                        'docker-compose >= 1.18.0',
                        'gitpython >= 2.1.3'],
      entry_points={'console_scripts': ['dip=dip.main:dip']})
