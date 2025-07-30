import json
import subprocess

import typer
from tabulate import tabulate

from src.modukit_binary import get_modukit_binary_path

list_app = typer.Typer(
    help="List all modules in the local environment. Use this command to view installed modules and their details."
)


def list_modules(ctx: typer.Context):
    modukit_binary = get_modukit_binary_path()
    result = subprocess.run(
        [modukit_binary, 'list', *(ctx.args or []), '-j'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        typer.echo(f"[modukit] Error running modukit list command: {result.stderr}")
        raise typer.Exit(code=result.returncode)

    typer.echo("[modukit] Parsing modkit output...")
    modukit_json = json.loads(result.stdout)
    modules = modukit_json.get("content", [])

    table = []
    headers = ["Name", "Version", "Description", "Author(s)", "License", "Homepage"]
    for mod in modules:
        table.append([
            mod.get("name", ""),
            mod.get("version", ""),
            mod.get("desc", ""),
            ", ".join(mod.get("author", [])),
            mod.get("license", ""),
            mod.get("homepage", "")
        ])

    typer.echo(tabulate(table, headers=headers, tablefmt="fancy_grid"))
    typer.echo(f"[modukit] Listed {len(modules)} module(s).")


list_app.command(
    name="list",
    help="List all modules in the local environment.",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)(list_modules)

list_app.command(
    name="ls",
    help="List all modules in the local environment.",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)(list_modules)
