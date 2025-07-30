import typer
try:
    from importlib.metadata import version as pkg_version
except ImportError:
    from importlib_metadata import version as pkg_version  # type: ignore

version_app = typer.Typer(
    help="Show the CLI version. Use this command to check the current version of the CLI."
)


@version_app.command(
    name="v",  # shortcut command name
    help="Show the CLI version."
)
def version():
    try:
        ver = pkg_version("modukit-dj")
        print(f"modukit-dj version {ver}")
    except Exception as e:
        print(f"Error reading installed package version: {e}")
