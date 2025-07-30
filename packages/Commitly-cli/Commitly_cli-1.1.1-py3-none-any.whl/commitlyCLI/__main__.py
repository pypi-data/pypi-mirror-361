
from commitlyCLI.cli import CommitlyCLI
from sys import platform
from os import system

def main():
    system('cls' if platform == 'win32' else 'clear')
    CommitlyCLI().run()

if __name__ == "__main__":
    main()