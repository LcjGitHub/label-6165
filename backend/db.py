"""SQLite 数据库初始化与连接管理。"""

import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "plants.db"


def get_db():
    """获取 SQLite 连接，行以 dict 形式返回。"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """创建表结构（若不存在），并执行必要的迁移。"""
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            variety TEXT NOT NULL DEFAULT '',
            purchase_date TEXT NOT NULL,
            location TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS repotting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS watering (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
        );
        """
    )

    cursor = conn.execute("PRAGMA table_info(plants)")
    columns = [col[1] for col in cursor.fetchall()]
    if "location" not in columns:
        conn.execute("ALTER TABLE plants ADD COLUMN location TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()


def row_to_dict(row):
    """将 sqlite3.Row 转为普通 dict。"""
    return dict(row) if row else None
