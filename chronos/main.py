import click
from datetime import datetime 
from pathlib import Path

from chronos.ui import print_error, print_success
from chronos.storage import load_data, add_event, log

CHRONOS_DIR = Path.home() / ".chronos"
CHRONOS_DIR.mkdir(parents=True, exist_ok=True)
CURRENT_FILE = CHRONOS_DIR / "current_activity.json"            # временный файл для записи текущей активности

@click.group()
def cli():
        """chronos --- трекер активности"""
        pass

@cli.command()
@click.argument("name")
def start(name): 
        """начать активность, запоминаем время старта"""
        import json
        from chronos.ui import print_start
        if not CURRENT_FILE.exists():
                CURRENT_FILE.write_text("{}")
        
        with CURRENT_FILE.open('r') as f:
                try:
                        current = json.load(f)
                except json.JSONDecodeError:
                        current = {}
        
        if current:
               print_error(f"активность '{current['name']}' уже запущена. сначала остановите её!")
               return
        
        start_time = datetime.now()

        new_activity = {
               "name": name,
               "start": start_time.isoformat()
        }

        with CURRENT_FILE.open("w") as f:
               json.dump(new_activity, f)
        
        print_start(f"started {name} at {start_time.strftime('%H:%M')}")
        log(f"started activity {name} at {start_time.isoformat()}")

@cli.command()
def stop():
        """завершить текущую активность, сохраняя duration и время окончания"""
        import json
        from chronos.utils import format_duration
        from chronos.ui import print_stop

        if not CURRENT_FILE.exists():
                click.echo("нет запущенной активности!")
                return
      
        with CURRENT_FILE.open('r') as f:
                try: 
                        current = json.load(f)
                except json.JSONDecodeError:
                       current = {}

        if not current:
                print_error("нет запущенной активности!")
                if CURRENT_FILE.exists(): CURRENT_FILE.unlink()         # удалить битый файл
                return

        end_time = datetime.now()
        start_time = datetime.fromisoformat(current["start"])
        duration = (end_time - start_time).total_seconds() / 3600       # время в часах

        # добавляем само событие 
        add_event(
               name=current["name"], 
               duration=duration, 
               start=current["start"], 
               end=end_time.isoformat()
        )

        CURRENT_FILE.unlink()

        print_stop(current["name"], format_duration(duration))
        log(f"stopped activity: {current["name"]}, duration {duration} h, end: {end_time.isoformat()}")

@cli.command()
def status():
        """показать текущую активную задачу и время в работе"""
        import json
        from chronos.utils import format_duration
        from chronos.ui import print_status, print_error # Импортируем консоль для красивого вывода
    
        if not CURRENT_FILE.exists():
                print_error("сейчас никакая активность не запущена!")
                return

        try:
                with CURRENT_FILE.open('r') as f:
                        current = json.load(f)
        except (json.JSONDecodeError, ValueError):
                current = {}

        if not current:
                print_error("сейчас никакая активность не запущена!")
                return

        # Считаем, сколько времени прошло с момента старта до СЕЙЧАС
        start_time = datetime.fromisoformat(current['start'])
        elapsed = (datetime.now() - start_time).total_seconds() / 3600
    
        print_status(
                name = current["name"],
                start_time_str = start_time.strftime("%H:%M:%S"),
                duration_str = format_duration(elapsed)
        )

@cli.command()
@click.argument("name")
@click.argument("time_str")
def add(name, time_str):
        """добавление активностью с заданной длительностью"""
        from chronos.utils import format_duration
        from chronos.ui import print_add

        def parse_duration(s: str) -> float:
                """преобразует строку 'чч:мм', 'чч,мм', 'чч.мм' или float в часы (float)"""
                try:
                        if "," in s:
                                hours, minutes = map(int, s.split(','))
                                duration = hours + minutes / 60
                        elif ':' in s:
                                hours, minutes = map(int, s.split(':'))
                                duration = hours + minutes / 60
                        elif '.' in s:
                                hours, minutes = map(int, s.split('.'))
                                duration = hours + minutes / 60
                        else: 
                                return float(s)
                        return hours + minutes / 60
                except ValueError:
                        raise ValueError("неправильный формат, используйте h:m, h.m, h,m или float (например 2:15)")
        try:
               duration = parse_duration(time_str)
        except ValueError as e:
               click.echo(str(e))
               return

        add_event(name=name, duration=duration)
        print_add(name, format_duration(duration))



@cli.command()
def show():
        """показать все записи"""
        from chronos.ui import show_table

        data = load_data()

        show_table(data)

if __name__ == "__main__":
    cli()