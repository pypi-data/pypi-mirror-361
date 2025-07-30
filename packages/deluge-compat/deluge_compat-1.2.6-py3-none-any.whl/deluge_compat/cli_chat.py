"""Interactive chat CLI for testing SalesIQ scripts."""

import json
from pathlib import Path
from typing import Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import run_deluge_script
from .salesiq.core import Message
from .salesiq.mocks import MockManager

console = Console()
chat_app = typer.Typer(help="Interactive chat for testing SalesIQ scripts")


@chat_app.command()
def chat_command(
    script_file: Path = typer.Argument(
        ...,
        help="Path to the Deluge SalesIQ script file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    visitor_mock_source: str = typer.Option(
        "faker",
        "--visitor-mock-source",
        help="Visitor mock source: faker, json, endpoint, none",
    ),
    visitor_mock_file: Path | None = typer.Option(
        None,
        "--visitor-mock-file",
        help="JSON file with visitor mock data",
    ),
    visitor_mock_endpoint: str | None = typer.Option(
        None,
        "--visitor-mock-endpoint",
        help="Endpoint URL for visitor mock data",
    ),
    message_mock_source: str = typer.Option(
        "interactive",
        "--message-mock-source",
        help="Message mock source: interactive, json, endpoint",
    ),
    message_mock_file: Path | None = typer.Option(
        None,
        "--message-mock-file",
        help="JSON file with message mock data",
    ),
    api_mock_source: str = typer.Option(
        "json",
        "--api-mock-source",
        help="API mock source: json, endpoint, passthrough",
    ),
    api_mock_file: Path | None = typer.Option(
        None,
        "--api-mock-file",
        help="JSON file with API response mock data",
    ),
    visitor_scenario: str | None = typer.Option(
        None,
        "--visitor-scenario",
        help="Visitor scenario name (for JSON mock files)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug output",
    ),
    session_limit: int = typer.Option(
        50,
        "--session-limit",
        help="Maximum number of messages in session",
    ),
) -> None:
    """Start an interactive chat session with a SalesIQ script."""

    try:
        # Build mock configuration
        mock_config = _build_mock_config(
            visitor_mock_source=visitor_mock_source,
            visitor_mock_file=visitor_mock_file,
            visitor_mock_endpoint=visitor_mock_endpoint,
            message_mock_source=message_mock_source,
            message_mock_file=message_mock_file,
            api_mock_source=api_mock_source,
            api_mock_file=api_mock_file,
        )

        # Initialize mock manager
        mock_manager = MockManager(mock_config)

        # Load the script
        script_content = script_file.read_text(encoding="utf-8")

        # Get visitor data
        visitor = mock_manager.get_visitor(visitor_scenario)

        # Show session header
        _show_session_header(visitor, mock_config, debug)

        # Start chat loop
        _run_chat_session(
            script_content=script_content,
            mock_manager=mock_manager,
            visitor=visitor,
            debug=debug,
            session_limit=session_limit,
        )

    except Exception as e:
        rprint(f"[red]Error starting chat session:[/red] {e}")
        if debug:
            import traceback

            rprint(f"[red]Traceback:[/red]\n{traceback.format_exc()}")
        raise typer.Exit(1) from e


def _build_mock_config(
    visitor_mock_source: str,
    visitor_mock_file: Path | None,
    visitor_mock_endpoint: str | None,
    message_mock_source: str,
    message_mock_file: Path | None,
    api_mock_source: str,
    api_mock_file: Path | None,
) -> dict[str, Any]:
    """Build mock configuration from CLI arguments."""
    config = {
        "visitor": {
            "mock_source": visitor_mock_source,
        },
        "message": {
            "mock_source": message_mock_source,
        },
        "api_responses": {
            "mock_source": api_mock_source,
        },
    }

    # Add visitor-specific config
    if visitor_mock_file:
        config["visitor"]["mock_file"] = str(visitor_mock_file)
    if visitor_mock_endpoint:
        config["visitor"]["mock_endpoint"] = visitor_mock_endpoint

    # Add message-specific config
    if message_mock_file:
        config["message"]["mock_file"] = str(message_mock_file)

    # Add API-specific config
    if api_mock_file:
        config["api_responses"]["mock_file"] = str(api_mock_file)

    return config


def _show_session_header(visitor, mock_config: dict[str, Any], debug: bool) -> None:
    """Display session information and visitor context."""

    # Create visitor info table
    visitor_table = Table(title="Visitor Context", show_header=False)
    visitor_table.add_column("Field", style="cyan")
    visitor_table.add_column("Value", style="white")

    # Add key visitor fields
    key_fields = [
        ("Name", visitor.get("name") or "Unknown"),
        ("Email", visitor.get("email") or "Not provided"),
        ("Phone", visitor.get("phone") or "Not provided"),
        ("State", visitor.get("state") or "Unknown"),
        ("City", visitor.get("city") or "Unknown"),
        ("Current Page", visitor.get("current_page_url") or "Unknown"),
        ("Conversation ID", visitor.get("active_conversation_id") or "Unknown"),
    ]

    for field, value in key_fields:
        visitor_table.add_row(field, str(value))

    console.print(visitor_table)

    if debug:
        # Show mock configuration
        config_panel = Panel(
            json.dumps(mock_config, indent=2), title="Mock Configuration", title_align="left"
        )
        console.print(config_panel)

    console.print()
    rprint("[bold green]Chat session started! Type 'end chat' to exit.[/bold green]")
    console.print()


def _run_chat_session(
    script_content: str,
    mock_manager: MockManager,
    visitor,
    debug: bool,
    session_limit: int,
) -> None:
    """Run the interactive chat session."""

    message_count = 0

    while message_count < session_limit:
        try:
            # Get next message
            if mock_manager.message_mock.source_type == "interactive":
                try:
                    user_input = console.input("[bold blue]You:[/bold blue] ")
                    if not user_input.strip():
                        continue
                except (EOFError, KeyboardInterrupt):
                    rprint("\n[yellow]Chat session ended.[/yellow]")
                    break
            else:
                user_input = mock_manager.get_message()
                rprint(f"[bold blue]You:[/bold blue] {user_input}")
                # If we get end chat from mock source, break immediately
                if user_input.lower() in ["end chat", "exit", "quit"]:
                    break

            # Check for exit conditions
            if user_input.lower() in ["end chat", "exit", "quit", "bye"]:
                rprint("[yellow]Chat session ended.[/yellow]")
                break

            # Create message object
            message = Message(user_input)

            # Build execution context
            context = {
                "visitor": visitor,
                "message": message,
                "zoho": _create_zoho_namespace(mock_manager),
            }

            if debug:
                rprint(f"[dim]DEBUG: Processing message: {user_input}[/dim]")

            # Execute the script
            response = run_deluge_script(script_content, **context)

            if debug:
                rprint(f"[dim]DEBUG: Script response: {response}[/dim]")

            # Process response
            _handle_bot_response(response, debug)

            message_count += 1

        except KeyboardInterrupt:
            rprint("\n[yellow]Chat session interrupted.[/yellow]")
            break
        except Exception as e:
            rprint(f"[red]Error processing message:[/red] {e}")
            if debug:
                import traceback

                rprint(f"[red]Traceback:[/red]\n{traceback.format_exc()}")

            # Continue the session unless it's a critical error
            continue

    if message_count >= session_limit:
        rprint(f"[yellow]Session limit reached ({session_limit} messages).[/yellow]")


def _create_zoho_namespace(mock_manager: MockManager) -> dict[str, Any]:
    """Create the zoho namespace with SalesIQ functions."""
    from .salesiq.functions import visitorsession_get, visitorsession_set

    # Mock invokeurl to use the API mock system
    def mock_invokeurl(
        url: str, type: str = "GET", body: Any = None, headers: dict | None = None
    ) -> dict[str, Any]:
        return mock_manager.mock_api_call(url, type, body)

    return {
        "salesiq": {
            "visitorsession": {
                "get": visitorsession_get,
                "set": visitorsession_set,
            }
        },
        "adminuserid": "admin@example.com",  # Mock admin user
        "invokeurl": mock_invokeurl,  # Override invokeurl with mock
    }


def _handle_bot_response(response, debug: bool) -> None:
    """Handle and display the bot's response."""

    if response is None:
        rprint("[red]Bot: No response generated.[/red]")
        return

    # Handle different response types
    if hasattr(response, "get"):
        # Map/Dict-like response
        action = response.get("action", "reply")
        replies = response.get("replies", [])

        if action == "forward":
            rprint("[bold yellow]Bot:[/bold yellow] [dim](Forwarding to human agent)[/dim]")
            if replies:
                for reply in replies:
                    rprint(f"[bold yellow]Bot:[/bold yellow] {reply}")
            return
        elif action == "end":
            if replies:
                for reply in replies:
                    rprint(f"[bold yellow]Bot:[/bold yellow] {reply}")
            rprint("[yellow](Chat ended by bot)[/yellow]")
            return
        else:
            # Default 'reply' action
            if replies:
                for reply in replies:
                    rprint(f"[bold yellow]Bot:[/bold yellow] {reply}")
            else:
                rprint("[bold yellow]Bot:[/bold yellow] I received your message.")
    else:
        # Simple string response
        rprint(f"[bold yellow]Bot:[/bold yellow] {response}")

    console.print()


def chat_main():
    """Entry point for deluge-chat command."""
    chat_app()


if __name__ == "__main__":
    chat_main()
