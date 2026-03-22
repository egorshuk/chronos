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
        """отображает список активности по дням"""
        from collections import defaultdict
        from chronos.utils import format_datetime, format_duration, get_date

        if not data:
                print_error("записей пока нет")
                return

        # групировка по дням
        grouped_data = defaultdict(list)
        for entry in data: 
                date = get_date(entry.get("start"))
                grouped_data[date].append(entry)

        for date in sorted(grouped_data.keys()):
                day_entries = grouped_data[date]

                table = Table(title=f"📅 дата: {date}", title_style="bold magenta", box=None)
                table.add_column("ID", style="magenta", justify="right")
                table.add_column("название", style="cyan", width=30)
                table.add_column("длительность", style="green")
                table.add_column("старт", style="dim")
                table.add_column("конец", style="dim")

                total_day_hours = 0.0

                for entry in day_entries:
                        duration = entry.get("duration") or 0.0
                        total_day_hours += duration
                        
                        duration_str = format_duration(duration) if duration else "-"

                        table.add_row(
                                str(entry.get("_id", "?")),
                                entry["name"] ,
                                duration_str,
                                format_datetime(entry.get("start")),
                                format_datetime(entry.get("end"))
                        )
                
                console.print(table)
                
                console.print(f"[bold white]Итого за день:[/bold white] [bold yellow]{format_duration(total_day_hours)}[/bold yellow]")
                console.print("-" * 40) # Разделитель между днями

def draw_timeline(data: list) -> None:
        """рисует визуальный таймлайн дня"""
        from chronos.utils import get_day_fraction, get_date, format_datetime
        from datetime import datetime

        if not data:
                print_error("нет данных для таймлайна")
        
        # первая запись 
        date_str = get_date(data[0]['start'])
        console.print(f"\n[bold]📈 Таймлайн за {date_str}:[/bold]")

        # печать шкалы
        console.print("[dim]00:00  03:00  06:00  09:00  12:00  15:00  18:00  21:00  24:00[/dim]")
        console.print("[dim]  └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘  [/dim]")

        WIDTH = 57 

        for entry in data:
                start_f = get_day_fraction(entry["start"])
                end_f = get_day_fraction(entry["end"])

                # считаем отступы
                start_pos = int(start_f * WIDTH)
                end_pos = int(end_f * WIDTH)
                length = max(1, end_pos - start_pos)

                # создаем полоску
                bar_background = "░" * start_pos
                bar_content = "█" * length
                tail_length = WIDTH - (start_pos + length)
                bar_tail = "░" * tail_length if tail_length > 0 else ""

                # Форматируем время начала и конца через нашу утилиту
                t_start = format_datetime(entry['start'])
                t_end = format_datetime(entry['end'])
        
                console.print(f"  {bar_background}[cyan]{bar_content}[/cyan]{bar_tail} [bold]{t_start}-{t_end}[/bold] {entry['name']}")
        console.print("")
