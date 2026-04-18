import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

sql = """
    CREATE TABLE IF NOT EXISTS task_type (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL,
        type_color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS task_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state_name TEXT UNIQUE NOT NULL,
        state_color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS preset_colors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        color_name TEXT UNIQUE NOT NULL,
        color_value TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        type_id INTEGER NOT NULL,
        state_id INTEGER NOT NULL,

        scheduled_start DATE,
        scheduled_end DATE,

        is_archived INTEGER DEFAULT 0,   -- 是否归档
        
        priority INTEGER DEFAULT 5,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (type_id) REFERENCES task_type(id),
        FOREIGN KEY (state_id) REFERENCES task_state(id)
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state_id);
"""

cur.executescript(sql)

# 预设一个空状态（灰色）
cur.execute("""
    INSERT OR IGNORE INTO task_state (state_name, state_color)
    VALUES (?, ?)
""", ("未设置", "#808080"))

# 预设一个空类型（灰色）
cur.execute("""
    INSERT OR IGNORE INTO task_type (type_name, type_color)
    VALUES (?, ?)
""", ("未设置", "#808080"))

# 开启外键约束
cur.execute("PRAGMA foreign_keys = ON;")

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully.")