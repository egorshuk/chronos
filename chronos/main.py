import click
from datetime import datetime 
from pathlib import Path

from chronos.ui import print_error, print_success
from chronos.storage import load_data, add_event, log, delete_event

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
@click.option("--start", "-s", help="время начала в формате чч:мм (например 17:00)")
def add(name, time_str, start):
        """
        добавление активностью с заданной длительностью
        
        flag start --- возможность указать время начала текущего дня
        """
        from chronos.utils import format_duration
        from chronos.ui import print_add
        from datetime import datetime, timedelta

        def parse_duration(s: str) -> float:
                """преобразует строку 'чч:мм', 'чч,мм', 'чч.мм' или float в часы (float)"""
                try:
                        t = s.replace(',', ':').replace('.', ':')
                        if ':' in t:
                                parts = t.split(':')
                                hours = int(parts[0])
                                minutes = int(parts[1]) if len(parts) > 1 else 0
                                return hours + minutes / 60
                        return float(t)
                except ValueError:
                        raise ValueError("неправильный формат, используйте h:m, h.m, h,m или float (например 2:15)")
        try:
               duration = parse_duration(time_str)
        except ValueError as e:
               print_error(str(e))
               return

        now = datetime.now()

        if start:       # если заявленно время начала
                try:
                        t_start = start.replace(',', ':').replace('.', ':')
                        h, m = map(int, t_start.split(':'))
                        
                        start_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)

                        if start_dt > now:
                                start_dt -= timedelta(days=1)

                        end_dt = start_dt + timedelta(hours=duration)
                except Exception:
                        print_error("неверный формат времени старта. используйте чч:мм!")
                        return
        else:
                end_dt = now 
                start_dt = end_dt - timedelta(hours=duration)

        add_event(
                name=name,
                duration=duration,
                start = start_dt.isoformat(),
                end = end_dt.isoformat()
                )
        print_add(name, format_duration(duration))      


@cli.command()
@click.argument("event_id", type=int)
def delete(event_id):
        """удалить запись по её ID (номеру в таблице)"""
        from chronos.ui import print_success, print_error

        success, deleted_entry = delete_event(event_id)

        if success:
                print_success(f"запись #{event_id} '{deleted_entry["name"]}' удалена")
        else:
                print_error(f"ошибка: запись c ID #{event_id} не найдена")


@cli.command()
@click.option("--today", "-t", is_flag=True, help="показать только записи за сегодня")
def show(today):
        """показать все записи"""
        from chronos.ui import show_table
        from chronos.utils import get_date
        from datetime import datetime

        data = load_data()

        for i, entry in enumerate(data):
                entry["_id"] = i + 1

        if today:
                current_date = datetime.now().strftime("%d.%m.%Y")
                data = [entry for entry in data if get_date(entry.get("start")) == current_date]

        show_table(data)


@cli.command()
def timeline():
        """визуализация таймлайна активностей за сегодня"""
        from chronos.ui import draw_timeline, print_error
        from chronos.utils import get_date
        from datetime import datetime

        data = load_data()

        today_str = datetime.now().strftime("%d.%m.%Y")
        day_data = [entry for entry in data if get_date(entry.get("start")) == today_str]

        if not day_data:
                print_error("за сегодня еще нет завершенных активностей")
                return
        
        day_data.sort(key=lambda x: x['start'])

        draw_timeline(day_data)


if __name__ == "__main__":
    cli()