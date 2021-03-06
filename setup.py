
from setuptools import setup, find_packages

setup(
    name='TempLogger',
    version='1.3.0',
    url='https://github.com/mkielg11/templogger',
    author='Mathias Rønholt Kielgast',
    author_email='m.roenholt@gmail.com',
    description='Logger and plotter of temperature over time',
    packages=find_packages(),
    scripts=['templogger/templogger_main.py', ],
)
