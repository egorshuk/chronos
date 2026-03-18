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