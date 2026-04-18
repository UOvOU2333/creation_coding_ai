from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from services import task_service, type_service, state_service

from chains.agent import trace


class UpdateTaskInput(BaseModel):
    task_id: int = Field(description="要更新的任务ID")
    task_name: Optional[str] = Field(default=None, description="新的任务名称")
    type_name: Optional[str] = Field(default=None, description="新的任务类型名称")
    state_name: Optional[str] = Field(default=None, description="新的任务状态名称")
    scheduled_start: Optional[str] = Field(default=None, description="新的开始日期（ISO格式）")
    scheduled_end: Optional[str] = Field(default=None, description="新的结束日期（ISO格式）")
    priority: Optional[int] = Field(default=None, ge=0, le=10, description="新的优先级")
    is_archived: Optional[int] = Field(default=None, description="是否归档，0或1")


@tool(args_schema=UpdateTaskInput)
def update_task(
    task_id: int,
    task_name: Optional[str] = None,
    type_name: Optional[str] = None,
    state_name: Optional[str] = None,
    scheduled_start: Optional[str] = None,
    scheduled_end: Optional[str] = None,
    priority: Optional[int] = None,
    is_archived: Optional[int] = None,
) -> str:
    """
    更新指定任务的字段。只更新提供的字段，未提供的保持不变。
    """

    trace("UseTool", "UpdateTask", task_name, level="info")
    trace("UpdateTask", "task_id, task_name, type_name, state_name, scheduled_start, scheduled_end, priority, is_archived", f"{task_id}, {task_name}, {type_name}, {state_name}, {scheduled_start}, {scheduled_end}, {priority}, {is_archived}", level="debug")

    # 检查任务是否存在
    existing = task_service.get_task_by_id(task_id)
    if existing is None:
        return f"错误：未找到 ID 为 {task_id} 的任务。"

    # 转换类型名称
    type_id = None
    if type_name:
        types = type_service.get_all_types()
        for t in types:
            if t["type_name"] == type_name:
                type_id = t["id"]
                break
        if type_id is None:
            return f"错误：未找到名为 '{type_name}' 的类型。"

    # 转换状态名称
    state_id = None
    if state_name:
        states = state_service.get_all_states()
        for s in states:
            if s["state_name"] == state_name:
                state_id = s["id"]
                break
        if state_id is None:
            return f"错误：未找到名为 '{state_name}' 的状态。"

    try:
        task_service.update_task(
            task_id=task_id,
            task_name=task_name,
            type_id=type_id,
            state_id=state_id,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            priority=priority,
            is_archived=is_archived,
        )
        return f"任务 ID {task_id} 更新成功。"
    except Exception as e:
        return f"更新任务时出错：{str(e)}"