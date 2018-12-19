from setuptools import setup

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Install CLIs using docker-compose',
    entry_points={
        'console_scripts': [
            'dip=dip.main:dip',
        ],
    },
    install_requires=[
        'click >= 6.7',
        'colored >= 1.3',
        'docker-compose >= 1.23',
        'python-dotenv >= 0.10',
        'gitpython >= 2.1',
    ],
    name='dip',
    packages=['dip'],
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/dip',
    use_scm_version=True)
