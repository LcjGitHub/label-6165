"""初始化种子数据：3 株植物，每株 2 条换盆记录。"""

from db import get_db, init_db


SEED_PLANTS = [
  {
    "name": "绿萝",
    "variety": "黄金葛",
    "purchase_date": "2023-03-15",
    "location": "客厅",
    "repotting": [
      {"date": "2023-06-10", "notes": "换入 15cm 陶盆，添加腐叶土"},
      {"date": "2024-09-20", "notes": "根系发达，升级至 20cm 盆"},
    ],
  },
  {
    "name": "多肉组合",
    "variety": "玉露 + 熊童子",
    "purchase_date": "2024-01-08",
    "location": "阳台",
    "repotting": [
      {"date": "2024-04-12", "notes": "更换颗粒土，增加排水孔"},
      {"date": "2025-02-28", "notes": "春季换盆，修剪老根"},
    ],
  },
  {
    "name": "龟背竹",
    "variety": "大叶龟背竹",
    "purchase_date": "2022-11-20",
    "location": "书房",
    "repotting": [
      {"date": "2023-05-05", "notes": "首次换盆，保留原土"},
      {"date": "2024-11-15", "notes": "换入深盆，添加缓释肥"},
    ],
  },
]


def seed_if_empty():
    """仅在数据库为空时写入种子数据。"""
    init_db()
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
    if count > 0:
        conn.close()
        return

    for plant in SEED_PLANTS:
        cursor = conn.execute(
            "INSERT INTO plants (name, variety, purchase_date, location) VALUES (?, ?, ?, ?)",
            (plant["name"], plant["variety"], plant["purchase_date"], plant["location"]),
        )
        plant_id = cursor.lastrowid
        for r in plant["repotting"]:
            conn.execute(
                "INSERT INTO repotting (plant_id, date, notes) VALUES (?, ?, ?)",
                (plant_id, r["date"], r["notes"]),
            )

    conn.commit()
    conn.close()
