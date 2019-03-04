import os
from setuptools import setup, find_packages

setup(
    name = "whatsapp-cli",
    version = "0.1.2",
    author = "Ritvik Saraf",
    author_email = "13ritvik@gmail.com",
    description = "CLI for whatsapp",
    long_description=open('README.rst').read(),
    license = "MIT",
    keywords = [ "whatsapp", "pushbullet", "whatsapp cli", "chat bots" ],
    url = "https://github.com/yausername/whatsapp-cli",
    packages=find_packages(),
    package_data={'whatsappCli.feed': ['data/*.json']},
    entry_points = {
        'console_scripts': ['whatsapp-cli=whatsappCli.__main__:main'],
    },
    install_requires=[
        'requests',
        'websocket-client',
        'click',
    ],
    classifiers=[
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "License :: OSI Approved :: MIT License",
    ],
)
