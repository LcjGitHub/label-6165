"""家庭盆栽换盆历史 — Flask API 服务。"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from db import get_db, init_db, row_to_dict
from seed import seed_if_empty

app = Flask(__name__)
CORS(app, origins=["http://localhost:7101", "http://127.0.0.1:7101"])


def validate_plant(data):
    """校验植物字段。"""
    errors = []
    name = (data.get("name") or "").strip()
    variety = (data.get("variety") or "").strip()
    purchase_date = (data.get("purchase_date") or "").strip()
    if not name:
        errors.append("名称不能为空")
    if not purchase_date:
        errors.append("购入日期不能为空")
    return errors, {"name": name, "variety": variety, "purchase_date": purchase_date}


def validate_repotting(data):
    """校验换盆记录字段。"""
    errors = []
    date = (data.get("date") or "").strip()
    notes = (data.get("notes") or "").strip()
    if not date:
        errors.append("换盆日期不能为空")
    return errors, {"date": date, "notes": notes}


@app.route("/api/plants", methods=["GET"])
def list_plants():
    """获取植物列表（含换盆次数）。"""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT p.*, COUNT(r.id) AS repotting_count
        FROM plants p
        LEFT JOIN repotting r ON r.plant_id = p.id
        GROUP BY p.id
        ORDER BY p.created_at DESC
        """
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


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
    conn.close()

    result = row_to_dict(plant)
    result["repotting"] = [row_to_dict(r) for r in repotting]
    return jsonify(result)


@app.route("/api/plants", methods=["POST"])
def create_plant():
    """创建植物。"""
    errors, fields = validate_plant(request.json or {})
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO plants (name, variety, purchase_date) VALUES (?, ?, ?)",
        (fields["name"], fields["variety"], fields["purchase_date"]),
    )
    plant_id = cursor.lastrowid
    conn.commit()
    plant = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(plant)), 201


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
        "UPDATE plants SET name = ?, variety = ?, purchase_date = ? WHERE id = ?",
        (fields["name"], fields["variety"], fields["purchase_date"], plant_id),
    )
    conn.commit()
    plant = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(plant))


@app.route("/api/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    """删除植物及其换盆记录。"""
    conn = get_db()
    existing = conn.execute("SELECT id FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "植物不存在"}), 404

    conn.execute("DELETE FROM repotting WHERE plant_id = ?", (plant_id,))
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
        "INSERT INTO repotting (plant_id, date, notes) VALUES (?, ?, ?)",
        (plant_id, fields["date"], fields["notes"]),
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
        "UPDATE repotting SET date = ?, notes = ? WHERE id = ?",
        (fields["date"], fields["notes"], repot_id),
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


if __name__ == "__main__":
    init_db()
    seed_if_empty()
    app.run(host="0.0.0.0", port=7000, debug=True)
