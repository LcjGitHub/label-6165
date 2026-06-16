import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import db


class TestCreatePlant:
    def test_create_plant_success(self, client):
        resp = client.post(
            "/api/plants",
            json={
                "name": "绿萝",
                "variety": "黄金葛",
                "purchase_date": "2024-01-15",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "绿萝"
        assert data["variety"] == "黄金葛"
        assert data["purchase_date"] == "2024-01-15"
        assert data["location"] == "客厅"
        assert data["repot_interval_months"] == 12
        assert "id" in data
        assert "created_at" in data

    def test_create_plant_optional_fields_default(self, client):
        resp = client.post(
            "/api/plants",
            json={
                "name": "多肉",
                "variety": "",
                "purchase_date": "2024-02-20",
                "location": "阳台",
                "repot_interval_months": 18,
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "多肉"
        assert data["variety"] == ""
        assert data["location"] == "阳台"

    def test_create_plant_validation_empty_name(self, client):
        resp = client.post(
            "/api/plants",
            json={
                "name": "",
                "variety": "品种",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_plant_validation_invalid_date(self, client):
        resp = client.post(
            "/api/plants",
            json={
                "name": "测试植物",
                "variety": "品种",
                "purchase_date": "invalid-date",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_plant_validation_invalid_interval(self, client):
        resp = client.post(
            "/api/plants",
            json={
                "name": "测试植物",
                "variety": "品种",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 0,
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_plant_missing_fields(self, client):
        resp = client.post("/api/plants", json={"name": "测试"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_plant_empty_body(self, client):
        resp = client.post("/api/plants", json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data


class TestGetPlantDetail:
    def test_get_plant_by_id_success(self, client):
        create_resp = client.post(
            "/api/plants",
            json={
                "name": "龟背竹",
                "variety": "大叶龟背竹",
                "purchase_date": "2023-06-10",
                "location": "书房",
                "repot_interval_months": 24,
            },
        )
        plant_id = create_resp.get_json()["id"]

        resp = client.get(f"/api/plants/{plant_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == plant_id
        assert data["name"] == "龟背竹"
        assert data["variety"] == "大叶龟背竹"
        assert "repotting" in data
        assert isinstance(data["repotting"], list)
        assert "watering" in data
        assert isinstance(data["watering"], list)

    def test_get_plant_with_repotting_records(self, client):
        create_resp = client.post(
            "/api/plants",
            json={
                "name": "君子兰",
                "variety": "大花君子兰",
                "purchase_date": "2023-03-01",
                "location": "阳台",
                "repot_interval_months": 12,
            },
        )
        plant_id = create_resp.get_json()["id"]

        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2023-09-15", "pot_diameter_cm": 18, "notes": "首次换盆"},
        )
        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-09-20", "pot_diameter_cm": 22, "notes": "第二次换盆"},
        )

        resp = client.get(f"/api/plants/{plant_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["repotting"]) == 2
        assert data["last_repotting_date"] == "2024-09-20"

    def test_get_plant_not_found(self, client):
        resp = client.get("/api/plants/99999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert data["error"] == "植物不存在"

    def test_get_plant_computed_fields(self, client):
        create_resp = client.post(
            "/api/plants",
            json={
                "name": "虎皮兰",
                "variety": "金边虎皮兰",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 18,
            },
        )
        plant_id = create_resp.get_json()["id"]

        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-01", "pot_diameter_cm": 20, "notes": "换盆记录"},
        )

        resp = client.get(f"/api/plants/{plant_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "days_since_last_repotting" in data
        assert "next_repotting_date" in data
        assert "is_overdue" in data


class TestListPlants:
    def test_list_plants_empty(self, client):
        resp = client.get("/api/plants")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_plants_with_data(self, client_with_seed):
        resp = client_with_seed.get("/api/plants")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_list_plants_with_location_filter(self, client_with_seed):
        resp = client_with_seed.get("/api/plants?location=客厅")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert all(plant["location"] == "客厅" for plant in data)

    def test_list_plants_with_invalid_location(self, client_with_seed):
        resp = client_with_seed.get("/api/plants?location=无效位置")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 3


class TestUpdatePlant:
    def test_update_plant_success(self, client_with_seed):
        resp = client_with_seed.put(
            "/api/plants/1",
            json={
                "name": "绿萝更新",
                "variety": "黄金葛更新",
                "purchase_date": "2023-04-01",
                "location": "阳台",
                "repot_interval_months": 9,
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "绿萝更新"
        assert data["variety"] == "黄金葛更新"
        assert data["location"] == "阳台"
        assert data["repot_interval_months"] == 9

    def test_update_plant_not_found(self, client):
        resp = client.put(
            "/api/plants/99999",
            json={
                "name": "测试",
                "variety": "品种",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

    def test_update_plant_validation_error(self, client_with_seed):
        resp = client_with_seed.put(
            "/api/plants/1",
            json={
                "name": "",
                "variety": "品种",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data


class TestDeletePlant:
    def test_delete_plant_success(self, client_with_seed):
        resp = client_with_seed.delete("/api/plants/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

        resp = client_with_seed.get("/api/plants/1")
        assert resp.status_code == 404

    def test_delete_plant_not_found(self, client):
        resp = client.delete("/api/plants/99999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

    def test_delete_plant_cascades_repotting_records(self, client):
        create_resp = client.post(
            "/api/plants",
            json={
                "name": "测试植物",
                "variety": "测试品种",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        plant_id = create_resp.get_json()["id"]

        r1 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-03-01", "pot_diameter_cm": 15, "notes": "记录1"},
        )
        r2 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-01", "pot_diameter_cm": 18, "notes": "记录2"},
        )
        repot_id_1 = r1.get_json()["id"]
        repot_id_2 = r2.get_json()["id"]

        conn = db.get_db()
        before_count = conn.execute(
            "SELECT COUNT(*) FROM repotting WHERE id IN (?, ?)",
            (repot_id_1, repot_id_2),
        ).fetchone()[0]
        conn.close()
        assert before_count == 2

        client.delete(f"/api/plants/{plant_id}")

        conn = db.get_db()
        after_count = conn.execute(
            "SELECT COUNT(*) FROM repotting WHERE id IN (?, ?)",
            (repot_id_1, repot_id_2),
        ).fetchone()[0]
        conn.close()
        assert after_count == 0

    def test_delete_plant_cascades_watering_records(self, client):
        create_resp = client.post(
            "/api/plants",
            json={
                "name": "测试植物",
                "variety": "测试品种",
                "purchase_date": "2024-01-01",
                "location": "客厅",
                "repot_interval_months": 12,
            },
        )
        plant_id = create_resp.get_json()["id"]

        client.post(
            f"/api/plants/{plant_id}/watering",
            json={"date": "2024-03-01", "notes": "浇水1"},
        )
        client.post(
            f"/api/plants/{plant_id}/watering",
            json={"date": "2024-03-05", "notes": "浇水2"},
        )

        resp = client.get(f"/api/plants/{plant_id}")
        before_watering_count = len(resp.get_json()["watering"])
        assert before_watering_count == 2

        client.delete(f"/api/plants/{plant_id}")

        conn = db.get_db()
        after_count = conn.execute(
            "SELECT COUNT(*) FROM watering WHERE plant_id = ?",
            (plant_id,),
        ).fetchone()[0]
        conn.close()
        assert after_count == 0

    def test_delete_plant_removes_from_list(self, client_with_seed):
        before_resp = client_with_seed.get("/api/plants")
        before_count = len(before_resp.get_json())

        client_with_seed.delete("/api/plants/1")

        after_resp = client_with_seed.get("/api/plants")
        after_count = len(after_resp.get_json())
        assert after_count == before_count - 1
