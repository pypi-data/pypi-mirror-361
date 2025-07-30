import typer

try:
    from importlib.metadata import version as pkg_version
except ImportError:
    from importlib_metadata import version as pkg_version  # type: ignore

version_app = typer.Typer(
    help="Show the CLI version. Use this command to check the current version of the CLI."
)


def version():
    try:
        ver = pkg_version("modukit-dj")
        print(f"modukit-dj version {ver}")
    except Exception as e:
        print(f"Error reading installed package version: {e}")


version_app.command(
    name="version",
    help="Show the CLI version."
)(version)

version_app.command(
    name="v",
    help="Show the CLI version."
)(version)
