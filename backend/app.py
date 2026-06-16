"""家庭盆栽换盆历史 — Flask API 服务。"""

from datetime import datetime, timedelta
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from db import get_db, init_db, row_to_dict
from seed import seed_if_empty

app = Flask(__name__)
CORS(app, origins=[
    r"http://localhost:*",
    r"http://127.0.0.1:*",
])

LOCATION_OPTIONS = {"客厅", "阳台", "卧室", "书房", "其他"}


def add_months(date_str, months):
    """在指定日期基础上增加月数，返回日期字符串。"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return d.replace(year=year, month=month, day=day).strftime("%Y-%m-%d")


def compute_repotting_info(plant_dict, last_repot_date):
    """计算换盆相关信息：距上次换盆天数、建议下次换盆日期、是否超期。"""
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
    """获取植物最近一次换盆日期。"""
    row = conn.execute(
        "SELECT date FROM repotting WHERE plant_id = ? ORDER BY date DESC, id DESC LIMIT 1",
        (plant_id,),
    ).fetchone()
    return row["date"] if row else None


def validate_plant(data):
    """校验植物字段。"""
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
    """校验换盆记录字段。"""
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
    """校验浇水记录字段。"""
    errors = []
    date = (data.get("date") or "").strip()
    notes = (data.get("notes") or "").strip()
    if not date:
        errors.append("浇水日期不能为空")
    return errors, {"date": date, "notes": notes}


@app.route("/api/plants", methods=["GET"])
def list_plants():
    """获取植物列表（含换盆次数和换盆提醒信息），支持按位置筛选。"""
    location = request.args.get("location", "").strip()
    conn = get_db()

    if location and location in LOCATION_OPTIONS:
        rows = conn.execute(
            """
            SELECT p.*, COUNT(r.id) AS repotting_count,
                   (SELECT MAX(date) FROM repotting WHERE plant_id = p.id) AS last_repotting_date
            FROM plants p
            LEFT JOIN repotting r ON r.plant_id = p.id
            WHERE p.location = ?
            GROUP BY p.id
            ORDER BY p.created_at DESC
            """,
            (location,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT p.*, COUNT(r.id) AS repotting_count,
                   (SELECT MAX(date) FROM repotting WHERE plant_id = p.id) AS last_repotting_date
            FROM plants p
            LEFT JOIN repotting r ON r.plant_id = p.id
            GROUP BY p.id
            ORDER BY p.created_at DESC
            """
        ).fetchall()

    result = []
    for row in rows:
        plant = row_to_dict(row)
        last_repot = plant.get("last_repotting_date")
        repot_info = compute_repotting_info(plant, last_repot)
        plant.update(repot_info)
        result.append(plant)

    conn.close()
    return jsonify(result)


@app.route("/api/plants/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    """获取植物详情及换盆时间线。"""
    conn = get_db()
    plant = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not plant:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    repotting = conn.execute(
        "SELECT * FROM repotting WHERE plant_id = ? ORDER BY date DESC, id DESC",
        (plant_id,),
    ).fetchall()
    watering = conn.execute(
        "SELECT * FROM watering WHERE plant_id = ? ORDER BY date DESC, id DESC",
        (plant_id,),
    ).fetchall()

    last_repot_date = repotting[0]["date"] if repotting else None
    result = row_to_dict(plant)
    result["last_repotting_date"] = last_repot_date
    repot_info = compute_repotting_info(result, last_repot_date)
    result.update(repot_info)
    result["repotting"] = [row_to_dict(r) for r in repotting]
    result["watering"] = [row_to_dict(w) for w in watering]
    conn.close()
    return jsonify(result)


@app.route("/api/plants", methods=["POST"])
def create_plant():
    """创建植物。"""
    errors, fields = validate_plant(request.json or {})
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO plants (name, variety, purchase_date, location, repot_interval_months) VALUES (?, ?, ?, ?, ?)",
        (fields["name"], fields["variety"], fields["purchase_date"], fields["location"], fields["repot_interval_months"]),
    )
    plant_id = cursor.lastrowid
    conn.commit()
    plant = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    last_repot = get_last_repotting_date(conn, plant_id)
    result = row_to_dict(plant)
    result["last_repotting_date"] = last_repot
    repot_info = compute_repotting_info(result, last_repot)
    result.update(repot_info)
    conn.close()
    return jsonify(result), 201


@app.route("/api/plants/<int:plant_id>", methods=["PUT"])
def update_plant(plant_id):
    """更新植物信息。"""
    errors, fields = validate_plant(request.json or {})
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    conn.execute(
        "UPDATE plants SET name = ?, variety = ?, purchase_date = ?, location = ?, repot_interval_months = ? WHERE id = ?",
        (fields["name"], fields["variety"], fields["purchase_date"], fields["location"], fields["repot_interval_months"], plant_id),
    )
    conn.commit()
    plant = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    last_repot = get_last_repotting_date(conn, plant_id)
    result = row_to_dict(plant)
    result["last_repotting_date"] = last_repot
    repot_info = compute_repotting_info(result, last_repot)
    result.update(repot_info)
    conn.close()
    return jsonify(result)


@app.route("/api/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    """删除植物及其换盆记录。"""
    conn = get_db()
    existing = conn.execute("SELECT id FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    conn.execute("DELETE FROM repotting WHERE plant_id = ?", (plant_id,))
    conn.execute("DELETE FROM watering WHERE plant_id = ?", (plant_id,))
    conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/plants/<int:plant_id>/repotting", methods=["POST"])
def create_repotting(plant_id):
    """为植物添加换盆记录。"""
    conn = get_db()
    existing = conn.execute("SELECT id FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    errors, fields = validate_repotting(request.json or {})
    if errors:
        conn.close()
        return jsonify({"errors": errors}), 400

    cursor = conn.execute(
        "INSERT INTO repotting (plant_id, date, pot_diameter_cm, notes) VALUES (?, ?, ?, ?)",
        (plant_id, fields["date"], fields["pot_diameter_cm"], fields["notes"]),
    )
    repot_id = cursor.lastrowid
    conn.commit()
    record = conn.execute("SELECT * FROM repotting WHERE id = ?", (repot_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(record)), 201


@app.route("/api/plants/<int:plant_id>/repotting/<int:repot_id>", methods=["PUT"])
def update_repotting(plant_id, repot_id):
    """更新换盆记录。"""
    errors, fields = validate_repotting(request.json or {})
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM repotting WHERE id = ? AND plant_id = ?",
        (repot_id, plant_id),
    ).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "换盆记录不存在"}), 404

    conn.execute(
        "UPDATE repotting SET date = ?, pot_diameter_cm = ?, notes = ? WHERE id = ?",
        (fields["date"], fields["pot_diameter_cm"], fields["notes"], repot_id),
    )
    conn.commit()
    record = conn.execute("SELECT * FROM repotting WHERE id = ?", (repot_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(record))


@app.route("/api/plants/<int:plant_id>/repotting/<int:repot_id>", methods=["DELETE"])
def delete_repotting(plant_id, repot_id):
    """删除换盆记录。"""
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM repotting WHERE id = ? AND plant_id = ?",
        (repot_id, plant_id),
    ).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "换盆记录不存在"}), 404

    conn.execute("DELETE FROM repotting WHERE id = ?", (repot_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/plants/<int:plant_id>/watering", methods=["GET"])
def list_watering(plant_id):
    """获取指定植物的全部浇水记录，按日期从新到旧排序。"""
    conn = get_db()
    existing = conn.execute("SELECT id FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    rows = conn.execute(
        "SELECT * FROM watering WHERE plant_id = ? ORDER BY date DESC, id DESC",
        (plant_id,),
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/plants/<int:plant_id>/watering", methods=["POST"])
def create_watering(plant_id):
    """为植物添加浇水记录。"""
    conn = get_db()
    existing = conn.execute("SELECT id FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    errors, fields = validate_watering(request.json or {})
    if errors:
        conn.close()
        return jsonify({"errors": errors}), 400

    cursor = conn.execute(
        "INSERT INTO watering (plant_id, date, notes) VALUES (?, ?, ?)",
        (plant_id, fields["date"], fields["notes"]),
    )
    watering_id = cursor.lastrowid
    conn.commit()
    record = conn.execute("SELECT * FROM watering WHERE id = ?", (watering_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(record)), 201


@app.route("/api/plants/<int:plant_id>/watering/<int:watering_id>", methods=["PUT"])
def update_watering(plant_id, watering_id):
    """更新浇水记录。"""
    errors, fields = validate_watering(request.json or {})
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM watering WHERE id = ? AND plant_id = ?",
        (watering_id, plant_id),
    ).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "浇水记录不存在"}), 404

    conn.execute(
        "UPDATE watering SET date = ?, notes = ? WHERE id = ?",
        (fields["date"], fields["notes"], watering_id),
    )
    conn.commit()
    record = conn.execute("SELECT * FROM watering WHERE id = ?", (watering_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(record))


@app.route("/api/plants/<int:plant_id>/watering/<int:watering_id>", methods=["DELETE"])
def delete_watering(plant_id, watering_id):
    """删除浇水记录。"""
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM watering WHERE id = ? AND plant_id = ?",
        (watering_id, plant_id),
    ).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "浇水记录不存在"}), 404

    conn.execute("DELETE FROM watering WHERE id = ?", (watering_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/export", methods=["GET"])
def export_plants():
    """导出全部植物及换盆记录为 CSV 文件供浏览器下载。"""
    import csv
    import io

    conn = get_db()
    plants = conn.execute("SELECT * FROM plants ORDER BY created_at DESC").fetchall()
    rows = []
    for plant in plants:
        p = row_to_dict(plant)
        repottings = conn.execute(
            "SELECT * FROM repotting WHERE plant_id = ? ORDER BY date DESC, id DESC",
            (p["id"],),
        ).fetchall()
        if repottings:
            for r in repottings:
                rd = row_to_dict(r)
                rows.append({
                    "name": p["name"],
                    "variety": p["variety"],
                    "purchase_date": p["purchase_date"],
                    "repotting_date": rd["date"],
                    "pot_diameter_cm": rd.get("pot_diameter_cm", "") or "",
                    "repotting_notes": rd["notes"],
                })
        else:
            rows.append({
                "name": p["name"],
                "variety": p["variety"],
                "purchase_date": p["purchase_date"],
                "repotting_date": "",
                "pot_diameter_cm": "",
                "repotting_notes": "",
            })
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["植物名称", "品种", "购入日期", "换盆日期", "盆径(厘米)", "换盆备注"])
    for row in rows:
        writer.writerow([
            row["name"],
            row["variety"],
            row["purchase_date"],
            row["repotting_date"],
            row["pot_diameter_cm"],
            row["repotting_notes"],
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig")
    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=plants_export.csv",
        },
    )


@app.route("/api/overview", methods=["GET"])
def get_overview():
    """获取养护概览统计数据。"""
    conn = get_db()

    plant_count = conn.execute("SELECT COUNT(*) AS count FROM plants").fetchone()["count"]
    total_repotting_count = conn.execute("SELECT COUNT(*) AS count FROM repotting").fetchone()["count"]

    last_repotting_row = conn.execute(
        """
        SELECT r.date, p.name AS plant_name
        FROM repotting r
        JOIN plants p ON r.plant_id = p.id
        ORDER BY r.date DESC, r.id DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    return jsonify({
        "plant_count": plant_count,
        "total_repotting_count": total_repotting_count,
        "last_repotting_date": last_repotting_row["date"] if last_repotting_row else None,
        "last_repotting_plant_name": last_repotting_row["plant_name"] if last_repotting_row else None,
    })


if __name__ == "__main__":
    init_db()
    seed_if_empty()
    app.run(host="0.0.0.0", port=7000, debug=True)
