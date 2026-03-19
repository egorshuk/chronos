import json
from datetime import datetime
from pathlib import Path

CHRONOS_DIR = Path.home() / ".chronos"
CHRONOS_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = CHRONOS_DIR / "data.json"   
LOG_FILE = CHRONOS_DIR / "chronos.log"

def load_data():
        if not DATA_FILE.exists():
                # создать файл, если его нет
                DATA_FILE.write_text("[]")
                return []
        try: 
                with open(DATA_FILE, "r") as f:
                        return json.load(f)
        except json.JSONDecodeError: 
                # если файл пуст, или повреждён
                DATA_FILE.write_text("[]")
                return []
        
def save_data(data):
        with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)

def log(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
def add_event(name: str, duration: float = None, start: str = None, end: str = None):
        """
        добавление активности в data.json
        :param name: название активности
        :param duration: длительность в часах 
        :param start: время начала в ISO string
        :param end: время окончания в ISO string
        """

        data = load_data()
        entry = {
                "name": name,
                "duration": float(duration) if duration is not None else None,
                "start": start,
                "end": end
        }
        data.append(entry)
        save_data(data)
        log(f"added event: {entry}")