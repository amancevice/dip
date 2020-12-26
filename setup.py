from setuptools import find_packages
from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
    ],
    description='Install CLIs using docker-compose',
    entry_points={'console_scripts': ['dip=dip.main:dip']},
    install_requires=[
        'click >= 6.7',
        'colored >= 1.3',
        'docker-compose >= 1.23',
        'python-dotenv >= 0.10',
        'gitpython >= 2.1',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='dip',
    packages=find_packages(exclude=['tests']),
    python_requires='>= 3.5',
    setup_requires=['setuptools_scm'],
    tests_require=[
        'flake8',
        'pytest',
        'pytest-cov',
    ],
    url='https://github.com/amancevice/dip',
    use_scm_version=True,
)
