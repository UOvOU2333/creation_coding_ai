import streamlit as st
from datetime import date

from services import task_service as taskDB

def createTask():
    types = taskDB.get_task_types()
    states = taskDB.get_task_states()

    type_dict = {t["type_name"]: t["id"] for t in types}
    state_dict = {s["state_name"]: s["id"] for s in states}

    # 使用两列布局让界面更紧凑
    col1, col2 = st.columns(2)

    with col1:
        task_name = st.text_input("任务名称")
        type_name = st.selectbox("任务类型", list(type_dict.keys()))
        state_name = st.selectbox("初始状态", list(state_dict.keys()))
        start = st.date_input("开始日期", value=date.today())

    with col2:
        end = st.date_input("结束日期（可选）", value=None)
        priority = st.slider("优先级", 0, 10, 5)

    if st.button("创建任务", key="createTask", type="primary", use_container_width=True):
        if not task_name:
            st.warning("请输入任务名称")
            return

        # 调用新的 create_task 方法（仅包含必要参数）
        taskDB.create_task(
            task_name=task_name,
            type_id=type_dict[type_name],
            state_id=state_dict[state_name],
            scheduled_start=start.isoformat() if start else None,
            scheduled_end=end.isoformat() if end else None,
            priority=priority
        )
        st.success("任务创建成功！")