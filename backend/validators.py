LOCATION_OPTIONS = {"客厅", "阳台", "卧室", "书房", "其他"}


def validate_plant(data):
    errors = []
    name = (data.get("name") or "").strip()
    variety = (data.get("variety") or "").strip()
    purchase_date = (data.get("purchase_date") or "").strip()
    location = (data.get("location") or "").strip()
    repot_interval_months = data.get("repot_interval_months")
    if not name:
        errors.append("名称不能为空")
    if not purchase_date:
        errors.append("购入日期不能为空")
    if not location:
        errors.append("位置不能为空")
    elif location not in LOCATION_OPTIONS:
        errors.append("位置必须是客厅、阳台、卧室、书房、其他中的一个")
    if repot_interval_months is not None:
        try:
            repot_interval_months = int(repot_interval_months)
            if repot_interval_months <= 0:
                errors.append("建议换盆间隔月数必须大于 0")
        except (ValueError, TypeError):
            errors.append("建议换盆间隔月数必须是数字")
    else:
        repot_interval_months = 12
    return errors, {
        "name": name,
        "variety": variety,
        "purchase_date": purchase_date,
        "location": location,
        "repot_interval_months": repot_interval_months,
    }


def validate_repotting(data):
    errors = []
    date = (data.get("date") or "").strip()
    notes = (data.get("notes") or "").strip()
    pot_diameter_cm = data.get("pot_diameter_cm")
    if not date:
        errors.append("换盆日期不能为空")
    if pot_diameter_cm is not None and pot_diameter_cm != "":
        try:
            pot_diameter_cm = int(pot_diameter_cm)
            if pot_diameter_cm <= 0:
                errors.append("盆径必须为正整数")
        except (ValueError, TypeError):
            errors.append("盆径必须为正整数")
    else:
        pot_diameter_cm = None
    return errors, {"date": date, "pot_diameter_cm": pot_diameter_cm, "notes": notes}


def validate_watering(data):
    errors = []
    date = (data.get("date") or "").strip()
    notes = (data.get("notes") or "").strip()
    if not date:
        errors.append("浇水日期不能为空")
    return errors, {"date": date, "notes": notes}
