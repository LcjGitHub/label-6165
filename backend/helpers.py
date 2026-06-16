from datetime import datetime

from db import get_db, row_to_dict


def add_months(date_str, months):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return d.replace(year=year, month=month, day=day).strftime("%Y-%m-%d")


def compute_repotting_info(plant_dict, last_repot_date):
    interval_months = plant_dict.get("repot_interval_months", 12)
    if not interval_months:
        interval_months = 12

    start_date = last_repot_date if last_repot_date else plant_dict.get("purchase_date")
    if not start_date:
        return {
            "days_since_last_repotting": None,
            "next_repotting_date": None,
            "is_overdue": False,
        }

    today = datetime.now().date()
    last_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    days_since = (today - last_date).days
    next_date = add_months(start_date, interval_months)
    next_dt = datetime.strptime(next_date, "%Y-%m-%d").date()
    is_overdue = today > next_dt

    return {
        "days_since_last_repotting": days_since,
        "next_repotting_date": next_date,
        "is_overdue": is_overdue,
    }


def get_last_repotting_date(conn, plant_id):
    row = conn.execute(
        "SELECT date FROM repotting WHERE plant_id = ? ORDER BY date DESC, id DESC LIMIT 1",
        (plant_id,),
    ).fetchone()
    return row["date"] if row else None
