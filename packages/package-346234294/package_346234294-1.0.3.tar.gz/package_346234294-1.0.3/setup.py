from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess



class CustomInstallCommand(install):
    def run(self):
        print("evil code exec while building package")     
        install.run(self)
setup(
    name='package_346234294',
    version='0.1',
    packages=find_packages(),
    install_requires=[
    ],
    cmdclass={
        'install': CustomInstallCommand
    }
)
