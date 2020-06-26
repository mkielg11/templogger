
from setuptools import setup, find_packages

setup(
    name='TempLogger',
    version='0.0.1',
    url='https://github.com/mypackage.git',
    author='Mathias Rønholt Kielgast',
    author_email='m.roenholt@gmail.com',
    description='Logger and plotter of temperature over time',
    packages=find_packages(),    
    install_requires=['numpy', 'plotly'],
)
