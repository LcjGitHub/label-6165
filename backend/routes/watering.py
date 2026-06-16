from flask import Blueprint, jsonify, request

from db import get_db, row_to_dict
from validators import validate_watering

watering_bp = Blueprint("watering", __name__, url_prefix="/api/plants")


@watering_bp.route("/<int:plant_id>/watering", methods=["GET"])
def list_watering(plant_id):
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


@watering_bp.route("/<int:plant_id>/watering", methods=["POST"])
def create_watering(plant_id):
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


@watering_bp.route("/<int:plant_id>/watering/<int:watering_id>", methods=["PUT"])
def update_watering(plant_id, watering_id):
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


@watering_bp.route("/<int:plant_id>/watering/<int:watering_id>", methods=["DELETE"])
def delete_watering(plant_id, watering_id):
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
