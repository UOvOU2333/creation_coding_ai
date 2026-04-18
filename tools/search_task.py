from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, List
from services import task_service, type_service, state_service

from chains.agent import trace


class SearchTaskInput(BaseModel):
    name_keyword: Optional[str] = Field(default=None, description="任务名称模糊匹配关键字")
    type_name: Optional[str] = Field(default=None, description="任务类型名称（精确匹配）")
    state_name: Optional[str] = Field(default=None, description="任务状态名称（精确匹配）")
    min_priority: Optional[int] = Field(default=None, ge=0, le=10, description="最低优先级")
    max_priority: Optional[int] = Field(default=None, ge=0, le=10, description="最高优先级")
    include_archived: bool = Field(default=False, description="是否包含已归档任务")


@tool(args_schema=SearchTaskInput)
def search_task(
    name_keyword: Optional[str] = None,
    type_name: Optional[str] = None,
    state_name: Optional[str] = None,
    min_priority: Optional[int] = None,
    max_priority: Optional[int] = None,
    include_archived: bool = False,
) -> str:
    """
    根据条件搜索任务，返回符合条件的任务列表。
    """

    trace("UseTool", "SearchTask", name_keyword, level="info")
    trace("SearchTask", "name_keyword, type_name, state_name, min_priority, max_priority, include_archived", f"{name_keyword}, {type_name}, {state_name}, {min_priority}, {max_priority}, {include_archived}", level="debug")

    # 转换类型名称为 type_id
    type_id = None
    if type_name:
        types = type_service.get_all_types()
        for t in types:
            if t["type_name"] == type_name:
                type_id = t["id"]
                break
        if type_id is None:
            return f"未找到名为 '{type_name}' 的类型。"

    # 转换状态名称为 state_id
    state_id = None
    if state_name:
        states = state_service.get_all_states()
        for s in states:
            if s["state_name"] == state_name:
                state_id = s["id"]
                break
        if state_id is None:
            return f"未找到名为 '{state_name}' 的状态。"

    tasks = task_service.get_tasks(
        type_id=type_id,
        state_id=state_id,
        name_keyword=name_keyword,
        min_priority=min_priority,
        max_priority=max_priority,
        include_archived=include_archived,
    )

    if not tasks:
        return "未找到符合条件的任务。"

    # 格式化输出
    lines = [f"找到 {len(tasks)} 个任务："]
    for t in tasks:
        lines.append(
            f"ID {t['id']}: {t['task_name']} | 类型: {t['type_name']} | 状态: {t['state_name']} | "
            f"优先级: {t['priority']} | 开始: {t['scheduled_start'] or '未设'} | 结束: {t['scheduled_end'] or '未设'}"
        )
    return "\n".join(lines)