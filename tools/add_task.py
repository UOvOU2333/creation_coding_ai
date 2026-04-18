from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from services import task_service

from chains.loger import trace


class AddTaskInput(BaseModel):
    task_name: str = Field(description="任务名称")
    type_name: str = Field(description="任务类型名称（必须已在 task_type 表中存在）")
    state_name: str = Field(description="初始状态名称（必须已在 task_state 表中存在）")
    scheduled_start: Optional[str] = Field(
        default=None, description="计划开始日期，格式 YYYY-MM-DD，例如 2025-01-01"
    )
    scheduled_end: Optional[str] = Field(
        default=None, description="计划结束日期，格式 YYYY-MM-DD，例如 2025-12-31"
    )
    priority: int = Field(default=5, ge=0, le=10, description="优先级，0-10 整数，默认 5")


@tool(args_schema=AddTaskInput)
def add_task(
    task_name: str,
    type_name: str,
    state_name: str,
    scheduled_start: Optional[str] = None,
    scheduled_end: Optional[str] = None,
    priority: int = 5,
) -> str:
    """
    创建一个新任务。

    需要提供任务名称、类型名称、状态名称。类型和状态必须已存在。
    可选的开始/结束日期（ISO 格式字符串），以及优先级。
    """

    trace("UseTool", "AddTask", task_name, level="info")
    trace("AddTask", "Input", f"task_name: {task_name}, type_name: {type_name}, state_name: {state_name}", level="debug")

    # 获取类型ID
    types = task_service.get_task_types()
    type_id = None
    for t in types:
        if t["type_name"] == type_name:
            type_id = t["id"]
            break
    if type_id is None:
        return f"错误：未找到名为 '{type_name}' 的任务类型。"

    # 获取状态ID
    states = task_service.get_task_states()
    state_id = None
    for s in states:
        if s["state_name"] == state_name:
            state_id = s["id"]
            break
    if state_id is None:
        return f"错误：未找到名为 '{state_name}' 的任务状态。"

    # 创建任务
    try:
        task_service.create_task(
            task_name=task_name,
            type_id=type_id,
            state_id=state_id,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            priority=priority,
            is_archived=0,
        )
        return f"任务 '{task_name}' 创建成功。"
    except Exception as e:
        return f"创建任务时出错：{str(e)}"