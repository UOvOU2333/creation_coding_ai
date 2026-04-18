import streamlit as st
from datetime import date

from services import task_service as taskDB

def updateTask():
    types = taskDB.get_task_types()
    states = taskDB.get_task_states()

    type_dict = {t["type_name"]: t["id"] for t in types}
    state_dict = {s["state_name"]: s["id"] for s in states}

    edit_task_id = st.session_state.get("edit_task_id")
    task_data = None

    col1, col2 = st.columns(2)

    with col1:
        col_id, col_name = st.columns(2)
        with col_id:
            task_id = st.number_input("任务编号", value=edit_task_id, step=1)

        # 根据当前输入的 task_id 查询任务
        if task_id:
            try:
                task_data = taskDB.get_task_by_id(int(task_id))
            except Exception:
                task_data = None

        task_exists = task_data is not None

        with col_name:
            task_name = st.text_input(
                "任务名称",
                value=task_data["task_name"] if task_data else ""
            )

        if not task_id:
            st.warning("请输入任务ID或在总列表中点击修改")
        else:
            if not task_exists:
                st.error("任务ID不存在")
            else:
                # 类型和状态选择
                col_type, col_state = st.columns(2)

                type_keys = list(type_dict.keys())
                state_keys = list(state_dict.keys())

                default_type = None
                default_state = None
                if task_data:
                    for k, v in type_dict.items():
                        if v == task_data["type_id"]:
                            default_type = k
                    for k, v in state_dict.items():
                        if v == task_data["state_id"]:
                            default_state = k

                with col_type:
                    type_name = st.selectbox(
                        "任务类型",
                        type_keys,
                        index=type_keys.index(default_type) if default_type else 0
                    )
                with col_state:
                    state_name = st.selectbox(
                        "初始状态",
                        state_keys,
                        index=state_keys.index(default_state) if default_state else 0
                    )

                # 日期选择
                col_start, col_end = st.columns(2)
                with col_start:
                    start = st.date_input(
                        "开始日期",
                        value=date.fromisoformat(task_data["scheduled_start"]) if task_data and task_data["scheduled_start"] else date.today()
                    )
                with col_end:
                    end = st.date_input(
                        "结束日期（可选）",
                        value=date.fromisoformat(task_data["scheduled_end"]) if task_data and task_data["scheduled_end"] else None
                    )

    with col2:
        if task_exists:
            priority = st.slider(
                "优先级",
                0, 10,
                value=task_data["priority"] if task_data else 5
            )

    if task_id and task_exists:
        if st.button("修改任务", key="updateTask", type="primary", use_container_width=True):
            if not task_name:
                st.warning("请输入任务名称")
                return

            # 调用 update_task 方法，只更新传入的字段
            taskDB.update_task(
                task_id=task_id,
                task_name=task_name,
                type_id=type_dict[type_name],
                state_id=state_dict[state_name],
                scheduled_start=start.isoformat() if start else None,
                scheduled_end=end.isoformat() if end else None,
                priority=priority
            )
            st.success("任务修改成功！")

        if st.button("删除任务", key="deleteTask", use_container_width=True):
            taskDB.delete_task(task_id)
            st.success("任务删除成功！")
            st.rerun()