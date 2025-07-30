import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import importlib.metadata
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="sc")  # ← name パラメータを明示
app.main = app.__call__       # ← CliRunner 対応エイリアス
app.name = "sc"

console = Console()


@app.command("init", help="プロジェクトの初期化スキャフォールドを生成します。")
def init_command():
    here = os.path.dirname(__file__)
    template_dir = os.path.join(here, "templates")
    cwd = os.getcwd()

    typer.echo(f"Initializing new project in {cwd} …")
    shutil.copytree(template_dir, cwd, dirs_exist_ok=True)
    typer.secho("Done! 🎉", fg=typer.colors.GREEN)


@app.command("version", help="Show the Solar Circuit CLI version")
def version_command():
    ver = importlib.metadata.version("solar-circuit-v2")
    typer.echo(f"solar-circuit-v2 version {ver}")


@app.command("new", help="新規ワークオーダーを作成します。")
def new_command(id: str = typer.Option(None, "--id", help="カスタムIDを指定する場合")):
    wo_dir = Path.cwd() / "work_orders"
    wo_dir.mkdir(exist_ok=True)

    if id:
        filename = f"{id}.md"
    else:
        today = datetime.now().strftime("%Y%m%d")
        existing = sorted(wo_dir.glob(f"WO-{today}-*.md"))
        next_no = len(existing) + 1
        filename = f"WO-{today}-{next_no:03d}.md"

    path = wo_dir / filename
    path.write_text("")
    console.print(f"Created new work order: {path}", style="green")


@app.command("save", help="Append today's learning to dev_memory.md")
def save_command():
    kb_dir = Path.cwd() / ".sc" / "knowledge_base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "dev_memory.md"

    today = datetime.now().strftime("%Y-%m-%d")
    header = f"\n\n## {today}\n\n"
    kb_file.touch(exist_ok=True)
    content = kb_file.read_text(encoding="utf-8")
    if not content.endswith(header):
        kb_file.write_text(content + header, encoding="utf-8")

    editor = os.environ.get("EDITOR", "vi")
    typer.echo("Opening editor to append today's memory…")
    subprocess.run([editor, str(kb_file)])
    typer.secho("Saved! 👍", fg=typer.colors.GREEN)


@app.command("status", help="プロジェクトのステータスを表示します。")
def status_command():
    cwd = Path.cwd()

    console.rule("[bold blue]Today's Memory[/]")
    mem_file = cwd / "dev_memory.md"
    if mem_file.exists():
        lines = mem_file.read_text(
            encoding="utf-8").splitlines()
        if lines:
            console.print(lines[-1])
        else:
            console.print("[italic]Memory file is empty.[/]")
    else:
        console.print("[italic]No memory file found.[/]")

    console.rule("[bold green]Open Work Orders[/]")
    wo_dir = cwd / "work_orders"
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("WO-ID", style="dim", width=12)
    table.add_column("Title")
    table.add_column("Status", width=10)
    if wo_dir.is_dir():
        for path in sorted(wo_dir.glob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            if lines and lines[0].strip():
                title = lines[0].lstrip("# ").strip() or "(no title)"
            else:
                title = "(no title)"
            status = "open"
            table.add_row(path.stem, title, status)
    console.print(table)

    console.rule("[bold yellow]Attachments / Outbound[/]")
    for d in ("attachments", "outbound"):
        dirp = cwd / d
        if dirp.is_dir():
            files = list(dirp.rglob("*"))
            total = sum(f.stat().st_size for f in files if f.is_file())
            console.print(f"{d}: {len(files)} files, {total/1024:.1f} KB")
        else:
            console.print(f"{d}: [italic]none[/]")


@app.command("attach", help="ファイルを attachments/ にコピーして添付します。")
def attach_command(
    path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    name: str = typer.Option(None, "--name", "-n", help="コピー先のファイル名を指定"),
):
    dest_dir = Path.cwd() / "attachments"
    dest_dir.mkdir(exist_ok=True)
    dest_name = name or path.name
    dest = dest_dir / dest_name
    shutil.copy(path, dest)
    console.print(f"Attached: {dest}", style="green")


@app.command("outbound", help="ファイルを outbound/ にコピーして外部送信用としてマークします。")
def outbound_command(
    path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    name: str = typer.Option(None, "--name", "-n", help="コピー先のファイル名を指定"),
):
    dest_dir = Path.cwd() / "outbound"
    dest_dir.mkdir(exist_ok=True)
    dest_name = name or path.name
    dest = dest_dir / dest_name
    shutil.copy(path, dest)
    console.print(f"Outbounded: {dest}", style="yellow")


@app.command("list", help="既存の Work Order を一覧表示します。")
def list_command():
    wo_dir = Path.cwd() / "work_orders"
    if not wo_dir.is_dir():
        typer.echo("No work orders")
        return

    files = sorted(wo_dir.glob("*.md"))
    if not files:
        typer.echo("No work orders")
        return

    for path in files:
        typer.echo(path.stem)


if __name__ == "__main__":
    app()
