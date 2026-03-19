from rich.console import Console
from rich.table import Table

console = Console()

def print_error(msg: str) -> None:
        """выводит сообщение об ошибки красным цветом"""
        console.print(f"[red]{msg}[/red]")

def print_success(msg: str) -> None:
        """выводит сообщение об успехе зеленым"""
        console.print(f"[green]{msg}[/green]")

def print_status(name: str, start_time_str: str, duration_str: str) -> None:
    """Выводит информацию о текущей активной задаче."""
    console.print(f"[bold blue]⚡ В работе:[/bold blue] {name}")
    console.print(f"[dim]Запущено в:[/dim] {start_time_str}")
    console.print(f"[dim]Прошло:[/dim] [bold cyan]{duration_str}[/bold cyan]")

def print_start(name: str) -> None:
        """выводит сообщение о начале активности."""
        console.print(f"[bold green]▶ started[/bold green] {name}")

def print_stop(name: str, duration: str) -> None:
        """выводит сообщение о завершении активности с длительностью."""
        console.print(f"[bold yellow]■ stopped[/bold yellow] {name}, duration {duration}")

def print_add(name: str, duration: str) -> None:
        """выводит сообщение о добавлении активности"""
        console.print(f"[green]✔[/green] {name} [cyan]{duration}[/cyan]")


def show_table(data: list) -> None:
        """
        отображает список активностей в виде таблицы.

        :param data: список словарей с ключами name, duration, start, end
        :param format_duration: функция для форматирования duration в 'чч:мм'
        """
        from chronos.utils import format_datetime, format_duration

        if not data:
                console.print("[red]no entries yet[/red]")
                return

        table = Table(title="chronos activities")

        table.add_column("name", style="cyan")
        table.add_column("duration", style="green")
        table.add_column("start", style="dim")
        table.add_column("end", style="dim")

        for entry in data:
                duration = entry.get("duration")
                duration_str = format_duration(duration) if duration else "-"

                table.add_row(
                        entry["name"],
                        duration_str,
                        format_datetime(entry.get("start")),
                        format_datetime(entry.get("end")),
                )

        console.print(table)