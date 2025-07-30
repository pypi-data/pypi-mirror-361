from argparse import ArgumentParser
from pathlib import Path
from commitly.commitly import Commitly, FORMAT_COMMIT, STYLE_COMMIT, RECOMMANDATION
from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from commitlyCLI.logo import LOGO, VERSION
from sys import platform
from os import system


class CommitlyCLI:
    def __init__(self):
        self.console = Console()
        self.parser = self._init_parser()
        self.options = self.parser.parse_args()
        self.commitly = Commitly(file_temp=self.options.path_file_temp)

    def _init_parser(self):
        parser = ArgumentParser(description="Automatically generate a commit message based on the provided diff.")

        parser.add_argument("-a", "--add", type=str, help="Add a file to the commit", nargs="+", default=".")
        parser.add_argument("-f", "--format", type=str, help="Add a file of format commit")
        parser.add_argument("-s", "--style", type=str, help="Add a file of style commit")
        parser.add_argument("-r", "--recommendation", type=str, help="Add a file of style commit")
        parser.add_argument("-p", "--push", action="store_true", help="Push the commit to the remote repository")
        parser.add_argument("-t", "--ticket", type=str, help="Add a ticket number to the commit message")
        parser.add_argument("--show-format", action="store_true", help="Show the format commit")
        parser.add_argument("--show-style", action="store_true", help="Show the style commit")
        parser.add_argument("--show-recommendation", action="store_true", help="Show the recommendation commit")
        parser.add_argument("--confirm", action="store_true", help="confirm the message of the commit")
        parser.add_argument("--fact", action="store_true", help="propose de factoriser le commit en plusieurs plus petits")
        parser.add_argument("--path-file-temp", help="Path of the temporary file", default="commit.txt")
        parser.add_argument("--del-temp", action="store_true", help="Delete the temporary file")
        parser.add_argument("-c", "--continue", dest="continues", action="store_true", help="Continue the commit")
        return parser

    def _load_file_content(self, path):
        return Path(path).read_text(encoding='utf-8').replace("ÿþ", "") if path and Path(path).exists() else None

    def _show_panels(self):
        if self.options.show_format:
            self.console.print(Panel.fit(self.console.render_str(FORMAT_COMMIT), title="Format commit"))
        if self.options.show_style:
            self.console.print(Panel.fit(self.console.render_str(STYLE_COMMIT), title="Style commit"))
        if self.options.show_recommendation:
            self.console.print(Panel.fit(self.console.render_str(RECOMMANDATION), title="recommendation commit"))
        exit()

    def _display_logo(self):
        self.console.print(
            Panel.fit(self.console.render_str(LOGO), subtitle="version " + VERSION, border_style="bold black"),
            justify="center"
        )

    def _display_commit_and_files(self, msg, files):
        self.console.print(Panel.fit(self.console.render_str(msg), title="Commit message"))
        table = [Panel(Text(file), border_style="bold green") for file in files[:3]]
        if len(files) > 3:
            table.append(Panel(f"+ {len(files) - 3} more files", border_style="bold blue"))
        self.console.print(Columns(table, equal=False))

    def _confirm_message(self, m, files, format_commit, style_commit, recommendation_commit):
        c = Prompt.ask(
            prompt="confirm the message of the commit ? ",
            default="y",
            show_default=True,
            show_choices=True,
            choices=["y", 'r', "n"],
        )

        if c.lower() == "r":
            if not recommendation_commit:
                recommendation_commit = ""    
            recommendation_commit += f'\n\nPour regenerate le message du commit, voici le message que tu a generé précédament :\n{m}'
            
            self.commitly.unstage(".")
            self.commitly.add(" ".join(files))
            
            return self.commitly.generate_commit_message(
                style_commit=style_commit,
                format_commit=format_commit,
                recommandation_commit=recommendation_commit,
                ticket=self.options.ticket,
            )

        if c.lower() != "y":
            if self.options.del_temp:
                Path(self.commitly.file_temp).unlink(missing_ok=True)
            if self.options.add != '!':
                self.commitly.unstage(', '.join(self.options.add))
            self.console.print("[bold red]❌  Commit message not confirmed. [/bold red]")
            return False

        return True

    def _commit_run(self, msg, files):
        msg_final = self._load_file_content(self.options.path_file_temp)
        if msg_final != msg:
            self.console.print('[yellow]⚠️  Commit message has been modified[/yellow], [green]new commit message:[/green]')
            self._display_commit_and_files(msg_final, files)
        
        self.commitly.commit()
        self.console.print("[green]✔️  Commit message committed.[/green]")

    def process_commit(self, msg, files):
        self._display_commit_and_files(msg, files)

        if not self.commitly.save_message_to_file(msg):
            self.console.print("[bold red]❌  Error saving commit message. [/bold red]")
            return

        if self.options.confirm:
            format_commit = self._load_file_content(self.options.format)
            style_commit = self._load_file_content(self.options.style)
            recommendation_commit = self._load_file_content(self.options.recommendation)
            regen_msg = self. _confirm_message(msg, files, format_commit, style_commit, recommendation_commit)
            if regen_msg == False:
                return
            if isinstance(regen_msg, dict):
                return self.process_commit(regen_msg["commit"], regen_msg['files'])
            
        if self.options.fact:
            self.commitly.unstage(".")
            self.commitly.add(" ".join(files))

        self._commit_run(msg, files)

        if self.options.push:
            self.commitly.push()
            self.console.print("[green]✔️  Commit message pushed.[/green]")

    def run(self):
        self._display_logo()

        if self.options.show_format or self.options.show_style or self.options.show_recommendation:
            self._show_panels()

        if self.options.add:
            add = ', '.join(self.options.add)
            cmd_status = self.commitly.add(add) if add != '!' else True

            if cmd_status:
                self.console.print("[green]✔️  File added to the commit.[/green]")

                if not self.options.continues:
                    msg = self.commitly.generate_commit_message(
                        style_commit=self._load_file_content(self.options.style),
                        format_commit=self._load_file_content(self.options.format),
                        recommandation_commit=self._load_file_content(self.options.recommendation),
                        ticket=self.options.ticket,
                        fact=self.options.fact
                    )
                else:
                    try:
                        with open(self.commitly.file_temp, "r", encoding="utf-8") as f:
                            msg = {'commit': f.read(), 'files': self.commitly.file_stage()}
                    except FileNotFoundError:
                        self.console.print(f"file {self.commitly.file_temp} not found.")
                        exit()

                if msg:
                    if isinstance(msg, dict):
                        msg = [msg]

                    self.console.print("[green]✔️  Commit message generated.[/green]")
                    if len(msg) > 1 and self.options.fact:
                        self.console.print("[bold cyan]🧩 Plusieurs commits proposés par factorisation :[/bold cyan]")
                       
                    for _ in msg:
                        self.process_commit(_['commit'], _['files'])
                        
                else:
                    self.console.print("[bold red]❌  Error generating commit message. [/bold red]")
            else:
                self.console.print("[bold red]❌  Error adding file to the commit. [/bold red]")
        else:
            self.console.print("[bold red]❌  No file provided. [/bold red]")


def main():
    system('cls' if platform == 'win32' else 'clear')
    CommitlyCLI().run()

if __name__ == "__main__":
    main()