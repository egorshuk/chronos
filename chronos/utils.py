def format_duration(hours: float) -> str:
       """переводит float часы в стороку 'чч:мм'"""
       total_minutes = round(hours * 60) # округление до минут
       h = total_minutes // 60
       m = total_minutes % 60
       return f"{h:02d}:{m:02d}"

def format_datetime(iso_str: str) -> str:
        """преобразование ISO string в чч:мм"""
        from datetime import datetime
        try:
                return datetime.fromisoformat(iso_str).strftime("%H:%M")
        except Exception:
                return "-"


def get_date(iso_str: str) -> str:
        """извлекает дату из ISO string"""
        from datetime import datetime
        try:
                return datetime.fromisoformat(iso_str).strftime("%d.%m.%Y")
        except Exception:
                return "unknown day"

def get_day_fraction(iso_str: str) -> float:
        """возвращает время в процентах от начала для (0.0 - 1.0)"""
        from datetime import datetime
        try:
                dt = datetime.fromisoformat(iso_str)
                return (dt.hour * 3600 + dt.minute * 60 + dt.second) / 86400
        except Exception:
                return 0.0
        
