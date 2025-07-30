
from commitlyCLI.cli import CommitlyCLI
from sys import platform
from os import system

if __name__ == "__main__":
    system('cls' if platform == 'win32' else 'clear')
    CommitlyCLI().run()