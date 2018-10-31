from setuptools import setup

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Install CLIs using docker-compose',
    entry_points={'console_scripts': ['dip=dip.main:dip']},
    install_requires=[
        'click >= 6.7.0',
        'colored >= 1.3.93',
        'docker-compose >= 1.23.0',
        'gitpython >= 2.1.3'],
    name='dip',
    packages=['dip'],
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/dip',
    use_scm_version=True)
