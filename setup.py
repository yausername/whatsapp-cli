import os
from setuptools import setup

setup(
    name = "whatsappCli",
    version = "0.0.1",
    author = "Ritvik Saraf",
    author_email = "13ritvik@gmail.com",
    description = "CLI for whatsapp",
    license = "MIT",
    keywords = [ "whatsapp", "pushbullet", "whatsapp cli", "chat bots" ],
    url = "https://github.com/yausername/whatsapp-cli",
    packages=['whatsapp-cli'],
    #entry_points = {
    #    'console_scripts': ['whatsapp-cli=whatsappCli'],
    #},
    #scripts=['whatsapp-cli/__main__.py'],
    classifiers=[
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "License :: OSI Approved :: MIT License",
    ],
)
