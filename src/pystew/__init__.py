import os
import pathlib
import shutil

import click
from rich import print
from sh import git, stow  # type: ignore

HOME = pathlib.Path.home()
STEW_REPOSITORY = os.getenv("STEW_REPOSITORY", str(HOME / ".dotfiles"))


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


@cli.command()
def status():
    """Get status of the git repository"""
    print(git("status", _cwd=STEW_REPOSITORY))  # type: ignore


@cli.command()
def sync():
    """Sync the git repository"""
    git("pull", _cwd=STEW_REPOSITORY)  # type: ignore
    git("push", _cwd=STEW_REPOSITORY)  # type: ignore


@cli.command()
def doctor():
    """Check stew configuration and dependencies"""

    if HOME is not None and HOME != "":
        print(f":white_check_mark: Home directory is defined to: {HOME}")
    else:
        print(
            ":x: Home directory is not defined. Please set the HOME environment variable."
        )

    if STEW_REPOSITORY is not None and STEW_REPOSITORY != "":
        print(f":white_check_mark: Stew repository is defined to: {STEW_REPOSITORY}")
    else:
        print(
            ":x: Stew repository is not defined. Please set the STEW_REPOSITORY environment variable."
        )

    if shutil.which("git") is not None:
        print(":white_check_mark: Git is installed.")
    else:
        print(":x: Git is not installed. Please install Git to use stew.")

    if shutil.which("stow") is not None:
        print(":white_check_mark: Stow is installed.")
    else:
        print(":x: Stow is not installed. Please install Stow to use stew.")


@cli.command()
@click.argument("packages", nargs=-1, required=True)
def link(package: tuple[str, ...]):
    """Link packages with stow"""
    for p in set(package):
        try:
            stow("-d", STEW_REPOSITORY, p)  # type: ignore
        except Exception as e:
            print(f":x: Failed to link package {p}: {e}")
            continue
        print(f":link: package {p} linked successfully.")


@cli.command()
def list():
    """List managed packages"""
    repo_path = pathlib.Path(STEW_REPOSITORY)
    if not repo_path.exists() or not repo_path.is_dir():
        print(f":x: The directory {STEW_REPOSITORY} does not exist or is not a folder.")
        os._exit(1)

    EXCLUDES = {".git", ".gitignore"}

    def print_tree(path: pathlib.Path, indent: int = 0):
        prefix = "  " * indent
        print(
            f"{prefix}{'[bold]' + path.name + '[/bold]' if indent == 0 else path.name}"
        )
        children = sorted(path.iterdir())
        if not children:
            print(f"{prefix}  (empty)")
        for child in children:
            if child.is_dir():
                print_tree(child, indent + 1)
            else:
                print(f"{'  ' * (indent + 1)}{child.name}")

    for item in sorted(repo_path.iterdir()):
        if item.is_dir() and item.name not in EXCLUDES:
            print_tree(item)


if __name__ == "__main__":
    cli()
