from datetime import datetime

def calculate_price(from_date: str, to_date: str, price_per_day: float) -> float:

    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")

    if to_dt < from_dt:
        raise ValueError("to_date must be after from_date")

    num_days = (to_dt - from_dt).days + 1
    total_price = num_days * price_per_day

    return total_price
