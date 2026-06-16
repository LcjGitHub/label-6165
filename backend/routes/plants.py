from flask import Blueprint, jsonify, request

from db import get_db, row_to_dict
from helpers import compute_repotting_info, get_last_repotting_date
from validators import LOCATION_OPTIONS, validate_plant

plants_bp = Blueprint("plants", __name__, url_prefix="/api/plants")


@plants_bp.route("", methods=["GET"])
def list_plants():
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


@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
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


@plants_bp.route("", methods=["POST"])
def create_plant():
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


@plants_bp.route("/<int:plant_id>", methods=["PUT"])
def update_plant(plant_id):
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


@plants_bp.route("/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
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
