from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from services import state_service

from chains.loger import trace


class UpdateStateInput(BaseModel):
    state_id: int = Field(description="要更新的状态ID")
    state_name: Optional[str] = Field(default=None, description="新的状态名称")
    state_color: Optional[str] = Field(default=None, description="新的颜色代码")


@tool(args_schema=UpdateStateInput)
def update_state(state_id: int, state_name: Optional[str] = None, state_color: Optional[str] = None) -> str:
    """
    更新任务状态的名称或颜色。
    """

    trace("UseTool", "UpdateState", state_name, level="info")
    trace("UpdateState", "state_id, state_name, state_color", f"{state_id}, {state_name}, {state_color}", level="debug")

    states = state_service.get_all_states()
    existing = None
    for s in states:
        if s["id"] == state_id:
            existing = s
            break
    if existing is None:
        return f"错误：未找到 ID 为 {state_id} 的状态。"

    new_name = state_name if state_name is not None else existing["state_name"]
    new_color = state_color if state_color is not None else existing["state_color"]

    try:
        state_service.update_state(state_id, new_name, new_color)
        return f"状态 ID {state_id} 更新成功。"
    except Exception as e:
        return f"更新状态时出错：{str(e)}"