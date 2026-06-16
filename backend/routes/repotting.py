from flask import Blueprint, jsonify, request

from db import get_db, row_to_dict
from validators import validate_repotting

repotting_bp = Blueprint("repotting", __name__, url_prefix="/api/plants")


@repotting_bp.route("/<int:plant_id>/repotting", methods=["POST"])
def create_repotting(plant_id):
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


@repotting_bp.route("/<int:plant_id>/repotting/<int:repot_id>", methods=["PUT"])
def update_repotting(plant_id, repot_id):
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


@repotting_bp.route("/<int:plant_id>/repotting/<int:repot_id>", methods=["DELETE"])
def delete_repotting(plant_id, repot_id):
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
