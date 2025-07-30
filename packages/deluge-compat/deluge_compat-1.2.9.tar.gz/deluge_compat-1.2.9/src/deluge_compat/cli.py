"""Command-line interface for deluge-compat."""

import sys
from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from . import run_deluge_script, translate_deluge_to_python

console = Console()

run_app = typer.Typer(help="Run Deluge scripts")
translate_app = typer.Typer(help="Translate Deluge scripts to Python")


@run_app.command()
def run_command(
    script_file: Path = typer.Argument(
        ...,
        help="Path to the Deluge script file to execute",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output result as JSON instead of pretty printing",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """Run a Deluge script file and display the result."""
    try:
        if verbose:
            rprint(f"[blue]Reading script from:[/blue] {script_file}")

        script_content = script_file.read_text(encoding="utf-8")

        if verbose:
            rprint("[blue]Executing Deluge script...[/blue]")

        result = run_deluge_script(script_content)

        if result is not None:
            if output_json:
                import json

                # Convert result to JSON-serializable format
                if hasattr(result, "__dict__"):
                    json_result = dict(result) if hasattr(result, "items") else str(result)
                else:
                    json_result = result
                print(json.dumps(json_result, indent=2))
            else:
                rprint(
                    Panel(
                        str(result),
                        title="[green]Script Result[/green]",
                        title_align="left",
                    )
                )
        else:
            if verbose:
                rprint("[yellow]Script completed with no return value[/yellow]")

    except Exception as e:
        rprint(f"[red]Error executing script:[/red] {e}")
        raise typer.Exit(1) from e


@translate_app.command()
def translate_command(
    script_file: Path = typer.Argument(
        ...,
        help="Path to the Deluge script file to translate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (defaults to <script_name>.py)",
    ),
    no_wrapper: bool = typer.Option(
        False,
        "--no-wrapper",
        help="Generate raw Python code without PEP 723 wrapper",
    ),
    pep723: bool = typer.Option(
        True,
        "--pep723/--no-pep723",
        help="Generate PEP 723 compatible script (default: True)",
    ),
    show_code: bool = typer.Option(
        False,
        "--show",
        "-s",
        help="Display the translated code in addition to saving it",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """Translate a Deluge script to Python code."""
    try:
        if verbose:
            rprint(f"[blue]Reading script from:[/blue] {script_file}")

        script_content = script_file.read_text(encoding="utf-8")

        if verbose:
            rprint("[blue]Translating Deluge script to Python...[/blue]")

        # Determine output file if not specified
        if output_file is None:
            output_file = script_file.with_suffix(".py")

        # Translate the script
        python_code = translate_deluge_to_python(
            script_content, wrap_in_function=not no_wrapper, pep723_compatible=pep723
        )

        # Write to output file
        output_file.write_text(python_code, encoding="utf-8")

        rprint(f"[green]✓ Translated script saved to:[/green] {output_file}")

        if show_code:
            rprint("\n[blue]Generated Python code:[/blue]")
            syntax = Syntax(python_code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Translated Code", title_align="left"))

        if verbose and not no_wrapper:
            rprint(f"[dim]Run with: python {output_file}[/dim]")
            if pep723:
                rprint(f"[dim]Or with PEP 723 runner: uv run {output_file}[/dim]")

    except Exception as e:
        rprint(f"[red]Error translating script:[/red] {e}")
        raise typer.Exit(1) from e


def run_main():
    """Entry point for deluge-run command."""
    run_app()


def translate_main():
    """Entry point for deluge-translate command."""
    translate_app()


if __name__ == "__main__":
    # For development testing
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "translate":
        sys.argv.pop(1)
        translate_main()
    else:
        run_main()
