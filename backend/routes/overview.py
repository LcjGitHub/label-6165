import csv
import io

from flask import Blueprint, Response, jsonify

from db import get_db, row_to_dict

overview_bp = Blueprint("overview", __name__, url_prefix="/api")


@overview_bp.route("/export", methods=["GET"])
def export_plants():
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


@overview_bp.route("/overview", methods=["GET"])
def get_overview():
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
