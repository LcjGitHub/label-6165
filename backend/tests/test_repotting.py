import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def create_test_plant(client, name="测试植物", location="客厅"):
    resp = client.post(
        "/api/plants",
        json={
            "name": name,
            "variety": "测试品种",
            "purchase_date": "2024-01-01",
            "location": location,
            "repot_interval_months": 12,
        },
    )
    return resp.get_json()["id"]


class TestCreateRepotting:
    def test_create_repotting_success(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={
                "date": "2024-06-15",
                "pot_diameter_cm": 20,
                "notes": "首次换盆，添加腐叶土",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["plant_id"] == plant_id
        assert data["date"] == "2024-06-15"
        assert data["pot_diameter_cm"] == 20
        assert data["notes"] == "首次换盆，添加腐叶土"
        assert "id" in data
        assert "created_at" in data

    def test_create_repotting_without_notes(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={
                "date": "2024-06-15",
                "pot_diameter_cm": 18,
                "notes": "",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["notes"] == ""

    def test_create_repotting_without_pot_diameter(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={
                "date": "2024-06-15",
                "pot_diameter_cm": None,
                "notes": "无直径记录",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["pot_diameter_cm"] is None

    def test_create_repotting_plant_not_found(self, client):
        resp = client.post(
            "/api/plants/99999/repotting",
            json={
                "date": "2024-06-15",
                "pot_diameter_cm": 20,
                "notes": "测试",
            },
        )
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert data["error"] == "植物不存在"

    def test_create_repotting_validation_empty_date(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={
                "date": "",
                "pot_diameter_cm": 20,
                "notes": "测试",
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_repotting_validation_invalid_date(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={
                "date": "invalid-date",
                "pot_diameter_cm": 20,
                "notes": "测试",
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_repotting_validation_invalid_pot_diameter(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={
                "date": "2024-06-15",
                "pot_diameter_cm": -5,
                "notes": "测试",
            },
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_repotting_empty_body(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(f"/api/plants/{plant_id}/repotting", json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_repotting_missing_date(self, client):
        plant_id = create_test_plant(client)

        resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"pot_diameter_cm": 20, "notes": "缺少日期"},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data

    def test_create_multiple_repottings_same_plant(self, client):
        plant_id = create_test_plant(client, name="多肉植物")

        r1 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-03-01", "pot_diameter_cm": 12, "notes": "第一次换盆"},
        )
        r2 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-09-01", "pot_diameter_cm": 15, "notes": "第二次换盆"},
        )

        assert r1.status_code == 201
        assert r2.status_code == 201

        plant_resp = client.get(f"/api/plants/{plant_id}")
        repottings = plant_resp.get_json()["repotting"]
        assert len(repottings) == 2
        assert repottings[0]["date"] == "2024-09-01"
        assert repottings[1]["date"] == "2024-03-01"


class TestUpdateRepotting:
    def test_update_repotting_success(self, client):
        plant_id = create_test_plant(client)

        create_resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-15", "pot_diameter_cm": 20, "notes": "原始备注"},
        )
        repot_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/plants/{plant_id}/repotting/{repot_id}",
            json={"date": "2024-07-01", "pot_diameter_cm": 22, "notes": "更新后的备注"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["date"] == "2024-07-01"
        assert data["pot_diameter_cm"] == 22
        assert data["notes"] == "更新后的备注"

    def test_update_repotting_not_found(self, client):
        plant_id = create_test_plant(client)

        resp = client.put(
            f"/api/plants/{plant_id}/repotting/99999",
            json={"date": "2024-07-01", "pot_diameter_cm": 22, "notes": "测试"},
        )
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert data["error"] == "换盆记录不存在"

    def test_update_repotting_wrong_plant_id(self, client):
        plant1_id = create_test_plant(client, name="植物1")
        plant2_id = create_test_plant(client, name="植物2")

        create_resp = client.post(
            f"/api/plants/{plant1_id}/repotting",
            json={"date": "2024-06-15", "pot_diameter_cm": 20, "notes": "测试"},
        )
        repot_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/plants/{plant2_id}/repotting/{repot_id}",
            json={"date": "2024-07-01", "pot_diameter_cm": 22, "notes": "更新"},
        )
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

    def test_update_repotting_validation_error(self, client):
        plant_id = create_test_plant(client)

        create_resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-15", "pot_diameter_cm": 20, "notes": "测试"},
        )
        repot_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/plants/{plant_id}/repotting/{repot_id}",
            json={"date": "", "pot_diameter_cm": 22, "notes": "更新"},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data


class TestDeleteRepotting:
    def test_delete_repotting_success(self, client):
        plant_id = create_test_plant(client)

        create_resp = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-15", "pot_diameter_cm": 20, "notes": "待删除"},
        )
        repot_id = create_resp.get_json()["id"]

        resp = client.delete(f"/api/plants/{plant_id}/repotting/{repot_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

        plant_resp = client.get(f"/api/plants/{plant_id}")
        repottings = plant_resp.get_json()["repotting"]
        assert not any(r["id"] == repot_id for r in repottings)

    def test_delete_repotting_not_found(self, client):
        plant_id = create_test_plant(client)

        resp = client.delete(f"/api/plants/{plant_id}/repotting/99999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert data["error"] == "换盆记录不存在"

    def test_delete_repotting_wrong_plant_id(self, client):
        plant1_id = create_test_plant(client, name="植物1")
        plant2_id = create_test_plant(client, name="植物2")

        create_resp = client.post(
            f"/api/plants/{plant1_id}/repotting",
            json={"date": "2024-06-15", "pot_diameter_cm": 20, "notes": "测试"},
        )
        repot_id = create_resp.get_json()["id"]

        resp = client.delete(f"/api/plants/{plant2_id}/repotting/{repot_id}")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

    def test_delete_one_repotting_keeps_others(self, client):
        plant_id = create_test_plant(client, name="龟背竹")

        r1 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-03-01", "pot_diameter_cm": 15, "notes": "记录1"},
        )
        r2 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-01", "pot_diameter_cm": 18, "notes": "记录2"},
        )
        r3 = client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-09-01", "pot_diameter_cm": 20, "notes": "记录3"},
        )

        r2_id = r2.get_json()["id"]
        client.delete(f"/api/plants/{plant_id}/repotting/{r2_id}")

        plant_resp = client.get(f"/api/plants/{plant_id}")
        repottings = plant_resp.get_json()["repotting"]
        assert len(repottings) == 2
        assert r1.get_json()["id"] in [r["id"] for r in repottings]
        assert r3.get_json()["id"] in [r["id"] for r in repottings]
        assert r2_id not in [r["id"] for r in repottings]


class TestRepottingInPlantDetail:
    def test_repotting_records_ordered_by_date_desc(self, client):
        plant_id = create_test_plant(client, name="月季")

        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-01-15", "pot_diameter_cm": 16, "notes": "最早"},
        )
        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-06-20", "pot_diameter_cm": 18, "notes": "中间"},
        )
        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-12-01", "pot_diameter_cm": 20, "notes": "最晚"},
        )

        resp = client.get(f"/api/plants/{plant_id}")
        data = resp.get_json()
        repottings = data["repotting"]
        assert len(repottings) == 3
        assert repottings[0]["date"] == "2024-12-01"
        assert repottings[1]["date"] == "2024-06-20"
        assert repottings[2]["date"] == "2024-01-15"

    def test_plant_without_repotting_records(self, client):
        plant_id = create_test_plant(client, name="无换盆记录植物")

        resp = client.get(f"/api/plants/{plant_id}")
        data = resp.get_json()
        assert isinstance(data["repotting"], list)
        assert len(data["repotting"]) == 0
        assert data["last_repotting_date"] is None

    def test_repotting_updates_last_repotting_date(self, client):
        plant_id = create_test_plant(client, name="吊兰")

        resp1 = client.get(f"/api/plants/{plant_id}")
        assert resp1.get_json()["last_repotting_date"] is None

        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-03-15", "pot_diameter_cm": 14, "notes": "第一次"},
        )
        resp2 = client.get(f"/api/plants/{plant_id}")
        assert resp2.get_json()["last_repotting_date"] == "2024-03-15"

        client.post(
            f"/api/plants/{plant_id}/repotting",
            json={"date": "2024-09-20", "pot_diameter_cm": 16, "notes": "第二次"},
        )
        resp3 = client.get(f"/api/plants/{plant_id}")
        assert resp3.get_json()["last_repotting_date"] == "2024-09-20"
