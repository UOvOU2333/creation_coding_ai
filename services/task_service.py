import sqlite3
from datetime import date
from config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# =========================
# 基础查询
# =========================

def get_task_types():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_type ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_task_states():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_state ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_task_by_id(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_task(task_id, task_name=None, type_id=None, state_id=None,
                scheduled_start=None, scheduled_end=None, priority=None, is_archived=None):
    """
    更新任务字段，只更新传入的非 None 参数
    """
    conn = get_conn()
    cur = conn.cursor()

    updates = []
    params = []

    if task_name is not None:
        updates.append("task_name = ?")
        params.append(task_name)
    if type_id is not None:
        updates.append("type_id = ?")
        params.append(type_id)
    if state_id is not None:
        updates.append("state_id = ?")
        params.append(state_id)
    if scheduled_start is not None:
        updates.append("scheduled_start = ?")
        params.append(scheduled_start)
    if scheduled_end is not None:
        updates.append("scheduled_end = ?")
        params.append(scheduled_end)
    if priority is not None:
        updates.append("priority = ?")
        params.append(priority)
    if is_archived is not None:
        updates.append("is_archived = ?")
        params.append(is_archived)

    if not updates:
        conn.close()
        return

    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    params.append(task_id)

    cur.execute(query, params)
    conn.commit()
    conn.close()

# =========================
# 任务操作
# =========================

def create_task(task_name, type_id, state_id,
                scheduled_start=None, scheduled_end=None,
                priority=5, is_archived=0):
    """
    创建新任务
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks
        (task_name, type_id, state_id, scheduled_start, scheduled_end, priority, is_archived)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task_name, type_id, state_id, scheduled_start, scheduled_end, priority, is_archived))

    conn.commit()
    conn.close()


def get_tasks(type_id=None, state_id=None, name_keyword=None,
                           min_priority=None, max_priority=None,
                           include_archived=False):
    """
    获取任务列表，支持筛选
    :param type_id: int or list, 任务类型ID
    :param state_id: int or list, 任务状态ID
    :param name_keyword: str, 任务名称模糊匹配
    :param min_priority: int, 最低优先级
    :param max_priority: int, 最高优先级
    :param include_archived: bool, 是否包含已归档任务
    :return: list of Row
    """
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT t.*, tt.type_name, tt.type_color, ts.state_name, ts.state_color
        FROM tasks t
        JOIN task_type tt ON t.type_id = tt.id
        JOIN task_state ts ON t.state_id = ts.id
        WHERE 1=1
    """
    params = []

    if not include_archived:
        query += " AND t.is_archived = 0"

    if type_id is not None:
        if isinstance(type_id, list):
            placeholders = ",".join("?" for _ in type_id)
            query += f" AND t.type_id IN ({placeholders})"
            params.extend(type_id)
        else:
            query += " AND t.type_id = ?"
            params.append(type_id)

    if state_id is not None:
        if isinstance(state_id, list):
            placeholders = ",".join("?" for _ in state_id)
            query += f" AND t.state_id IN ({placeholders})"
            params.extend(state_id)
        else:
            query += " AND t.state_id = ?"
            params.append(state_id)

    if name_keyword:
        query += " AND t.task_name LIKE ?"
        params.append(f"%{name_keyword}%")

    if min_priority is not None:
        query += " AND t.priority >= ?"
        params.append(min_priority)

    if max_priority is not None:
        query += " AND t.priority <= ?"
        params.append(max_priority)

    query += " ORDER BY t.priority DESC, t.id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_task(task_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()