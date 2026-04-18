import streamlit as st
import datetime

from services import task_service as taskDB
from services import type_service as typeDB
from services import state_service as stateDB
from pages.subPages.widgets.capsule import render_capsule

def showAllTasks():
    # ===== 筛选控件 =====
    type_list = typeDB.get_all_types()
    state_list = stateDB.get_all_states()
    
    type_options = ["全部"] + [t["type_name"] for t in type_list]
    state_options = ["全部"] + [s["state_name"] for s in state_list]

    col_filter1, col_filter2, col_sort1, col_sort2, col_blank, col_filter3, col_filter4 = st.columns([10,10,10,10,1,10,20])

    with col_filter1:
        selected_type = st.selectbox("类型筛选", type_options)
        type_id = None
        if selected_type != "全部":
            type_id = next(t["id"] for t in type_list if t["type_name"] == selected_type)

    with col_filter2:
        selected_state = st.selectbox("状态筛选", state_options)
        state_id = None
        if selected_state != "全部":
            state_id = next(s["id"] for s in state_list if s["state_name"] == selected_state)

    with col_filter3:
        name_keyword = st.text_input("任务名关键字")

    with col_filter4:
        min_priority, max_priority = st.slider("优先级范围", 0, 10, (0, 10))

    # ===== 排序控件 =====
    with col_sort1:
        sort_field = st.selectbox("排序字段", ["优先级", "创建时间", "任务名称"])
    with col_sort2:
        sort_order = st.selectbox("排序方式", ["降序", "升序"])

    # ===== 获取任务 =====
    tasks = taskDB.get_tasks(
        type_id=type_id,
        state_id=state_id,
        name_keyword=name_keyword.strip() if name_keyword else None,
        min_priority=min_priority,
        max_priority=max_priority
    )

    # ===== 前端排序 =====
    if sort_field == "优先级":
        key = "priority"
    elif sort_field == "创建时间":
        key = "created_at"
    else:
        key = "task_name"
    reverse = True if sort_order == "降序" else False
    tasks = sorted(tasks, key=lambda x: x[key], reverse=reverse)

    if not tasks:
        st.info("暂无任务")
        return

    # ===== 展示任务 =====
    st.divider()
    for t in tasks:
        type_color = t["type_color"] if t["type_color"] else "#999999"
        state_color = t["state_color"] if t["state_color"] else "#999999"

        col1, col2, col3, col_blank, col4 = st.columns([6, 6, 4, 3, 3])

        with col1:
            st.markdown(f"""
            <div style="font-size:25px;font-weight:600;margin:2px;margin-top:0">
                {t["task_name"]}
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                {render_capsule(t["type_name"], type_color)}{render_capsule(t["state_name"], state_color)}
            """, unsafe_allow_html=True)

        with col2:
            # 优先级：5星制（支持半星）
            raw_priority = t["priority"] if t["priority"] is not None else 0
            raw_priority = max(0, min(int(raw_priority), 10))
            full_stars = raw_priority // 2
            has_half = (raw_priority % 2) == 1
            empty_stars = 5 - full_stars - (1 if has_half else 0)
            stars_html = ""
            for _ in range(full_stars):
                stars_html += "<span style='color:#FFD700;font-size:20px;'>★</span>"
            if has_half:
                stars_html += """
                <span style='
                    font-size:20px;
                    background: linear-gradient(90deg, #FFD700 50%, #DDDDDD 50%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                '>★</span>
                """
            for _ in range(empty_stars):
                stars_html += "<span style='color:#DDDDDD;font-size:20px;'>★</span>"
            st.markdown(f"<div style='margin-bottom:6px;'>{stars_html}</div>", unsafe_allow_html=True)

        with col3:
            # 显示日期范围
            start_str = t["scheduled_start"] if t["scheduled_start"] else "无"
            end_str = t["scheduled_end"] if t["scheduled_end"] else "无"
            st.write(f"{start_str} ～ {end_str}")

        with col4:
            if st.button("修改", key=f"edit_{t['id']}", use_container_width=True):
                st.session_state["edit_task_id"] = t["id"]
                st.success("已保存")

        with st.expander("任务详情", expanded=False):
            col_id, col_create = st.columns(2)
            with col_id:
                st.write("ID：" + str(t['id']))
            with col_create:
                created_at = t['created_at']
                if hasattr(created_at, 'strftime'):
                    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                st.write("创建时间：" + str(created_at))

        st.divider()


def todayTasks():
    """
    今日任务：展示当前未归档且处于有效日期范围内的任务。
    """
    today = datetime.date.today().isoformat()
    tasks = taskDB.get_tasks(include_archived=False)

    # 筛选出今天在 scheduled_start ~ scheduled_end 范围内的任务
    active_tasks = []
    for t in tasks:
        start = t["scheduled_start"]
        end = t["scheduled_end"]
        if start and start > today:
            continue
        if end and end < today:
            continue
        active_tasks.append(t)

    if not active_tasks:
        st.info("今天没有待办任务 🎉")
        return

    st.divider()
    for t in active_tasks:
        type_color = t["type_color"] if t["type_color"] else "#999999"
        state_color = t["state_color"] if t["state_color"] else "#999999"

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"""
            <div style="font-size:25px;font-weight:600;margin-bottom:6px;">
                {t['task_name']}
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                {render_capsule(t['type_name'], type_color)}{render_capsule(t['state_name'], state_color)}
            """, unsafe_allow_html=True)

        with col2:
            # 优先级：5星制（支持半星）
            raw_priority = t["priority"] if t["priority"] is not None else 0
            raw_priority = max(0, min(int(raw_priority), 10))
            full_stars = raw_priority // 2
            has_half = (raw_priority % 2) == 1
            empty_stars = 5 - full_stars - (1 if has_half else 0)
            stars_html = ""
            for _ in range(full_stars):
                stars_html += "<span style='color:#FFD700;font-size:20px;'>★</span>"
            if has_half:
                stars_html += """
                <span style='
                    font-size:20px;
                    background: linear-gradient(90deg, #FFD700 50%, #DDDDDD 50%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                '>★</span>
                """
            for _ in range(empty_stars):
                stars_html += "<span style='color:#DDDDDD;font-size:20px;'>★</span>"
            st.markdown(f"<div style='margin-bottom:6px;'>{stars_html}</div>", unsafe_allow_html=True)
        
            if st.button("修改", key=f"edit_{t['id']}", use_container_width=True):
                st.session_state["edit_task_id"] = t["id"]
                st.switch_page("pages/managingPage.py")

        st.divider()


def overview():
    """
    概览：展示未来5天内计划开始的任务（基于 scheduled_start）
    """
    today = datetime.date.today()
    future_days = [today + datetime.timedelta(days=i) for i in range(5)]

    cols = st.columns(5)
    for i, day in enumerate(future_days):
        with cols[i]:
            st.markdown(f"### {day.strftime('%m-%d %a')}")
            # 获取所有未归档任务
            all_tasks = taskDB.get_tasks(include_archived=False)
            # 筛选 scheduled_start 等于当天
            day_tasks = [t for t in all_tasks if (t["scheduled_start"] == day.isoformat() or ((t["scheduled_start"] <= day.isoformat() and t["scheduled_end"] >= day.isoformat()) if t["scheduled_end"] else False))]

            if not day_tasks:
                st.write("无任务")
            else:
                for t in day_tasks:
                    type_color = t["type_color"] if t["type_color"] else "#999999"
                    bars_html = f'''
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 8px; height: 20px; background-color: {type_color}; border-radius: 4px;"></div>
                        <div style="font-weight: 500; white-space: nowrap;">{t['task_name']}</div>
                    </div>
                    '''
                    st.markdown(bars_html, unsafe_allow_html=True)