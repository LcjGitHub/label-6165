import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import db
from app import app
from seed import seed_if_empty


@pytest.fixture
def client():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_plants.db"

    original_db_path = db.DB_PATH
    db.DB_PATH = db_path
    db.DB_DIR = db_path.parent

    try:
        db.init_db()
        seed_if_empty()

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client
    finally:
        db.DB_PATH = original_db_path
        db.DB_DIR = original_db_path.parent
        if db_path.exists():
            db_path.unlink()


def test_list_plants(client):
    resp = client.get("/api/plants")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_get_plant_detail(client):
    resp = client.get("/api/plants/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "name" in data
    assert "repotting" in data
    assert isinstance(data["repotting"], list)


def test_get_plant_not_found(client):
    resp = client.get("/api/plants/9999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_create_plant(client):
    resp = client.post(
        "/api/plants",
        json={
            "name": "测试植物",
            "variety": "测试品种",
            "purchase_date": "2024-01-01",
            "location": "客厅",
            "repot_interval_months": 12,
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "测试植物"
    assert data["variety"] == "测试品种"


def test_create_plant_validation_error(client):
    resp = client.post("/api/plants", json={"name": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data


def test_update_plant(client):
    resp = client.put(
        "/api/plants/1",
        json={
            "name": "更新后名称",
            "variety": "更新后品种",
            "purchase_date": "2024-02-01",
            "location": "阳台",
            "repot_interval_months": 6,
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "更新后名称"


def test_delete_plant(client):
    resp = client.delete("/api/plants/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True

    resp = client.get("/api/plants/1")
    assert resp.status_code == 404


def test_create_repotting(client):
    resp = client.post(
        "/api/plants/1/repotting",
        json={
            "date": "2024-06-01",
            "pot_diameter_cm": 20,
            "notes": "测试换盆备注",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["date"] == "2024-06-01"


def test_overview(client):
    resp = client.get("/api/overview")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "plant_count" in data
    assert "total_repotting_count" in data
    assert data["plant_count"] >= 3


def test_export_csv(client):
    resp = client.get("/api/export")
    assert resp.status_code == 200
    assert resp.content_type.startswith("text/csv")
    assert "plants_export.csv" in resp.headers.get("Content-Disposition", "")
    content = resp.get_data(as_text=True)
    assert "植物名称" in content
    assert "品种" in content


def test_list_plants_with_location_filter(client):
    resp = client.get("/api/plants?location=客厅")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_create_watering(client):
    resp = client.post(
        "/api/plants/1/watering",
        json={
            "date": "2024-06-15",
            "notes": "测试浇水备注",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["date"] == "2024-06-15"


if __name__ == "__main__":
    exit_code = pytest.main([__file__, "-v"])
    sys.exit(exit_code)
