"""code-roast CLI."""

from __future__ import annotations

import sys
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from roast.engine import roast_code

app = typer.Typer(name="roast", help="Brutally honest code review from a senior engineer who has seen things.")
console = Console()


def _detect_language(path: str) -> str:
    ext_map = {
        ".py": "python", ".ts": "typescript", ".js": "javascript",
        ".go": "go", ".rs": "rust", ".java": "java", ".rb": "ruby",
        ".cs": "csharp", ".cpp": "cpp", ".sh": "bash",
    }
    return ext_map.get(Path(path).suffix.lower(), "unknown")


@app.command()
def main(
    file: str = typer.Argument("", help="File to roast (or pipe via stdin)"),
    language: str = typer.Option("", "--language", "-l", help="Language hint"),
    mercy: bool = typer.Option(False, "--mercy", "-m", help="Slightly less brutal"),
    issues_only: bool = typer.Option(False, "--issues", "-i", help="Show specific issues only"),
) -> None:
    """Submit code for a brutally honest review."""
    code = ""

    if file and Path(file).exists():
        code = Path(file).read_text(errors="ignore")
        if not language:
            language = _detect_language(file)
    elif not sys.stdin.isatty():
        code = sys.stdin.read()
    else:
        console.print("[red]Error:[/red] Provide a file path or pipe code via stdin.")
        console.print("  [dim]Example: cat my_code.py | roast[/dim]")
        raise typer.Exit(1)

    if not code.strip():
        console.print("[yellow]Nothing to roast — empty input.[/yellow]")
        raise typer.Exit(0)

    language = language or "unknown"

    console.print(f"\n[dim]Submitting {len(code.splitlines())} lines of {language} to the roast...[/dim]\n")

    result = roast_code(code, language, mercy)

    console.print(Panel.fit(
        f"[bold]{result.roast}[/bold]",
        title=f"Code Roast — {language} ({result.line_count} lines)",
        border_style="red",
        padding=(1, 2),
    ))

    if result.specific_issues:
        console.print()
        console.print(Rule("[dim]Specific grievances[/dim]", style="dim"))
        for issue in result.specific_issues:
            console.print(f"  [red]✗[/red] {issue}")

    console.print()
    console.print(f"  Score: [bold]{result.score}[/bold]")
    if result.verdict:
        console.print(f"  Verdict: [dim italic]{result.verdict}[/dim italic]")
    console.print()


if __name__ == "__main__":
    app()