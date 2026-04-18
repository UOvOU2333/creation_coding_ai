from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from services import state_service

from chains.agent import trace


class SearchStateInput(BaseModel):
    name_keyword: Optional[str] = Field(default=None, description="状态名称模糊匹配关键字")


@tool(args_schema=SearchStateInput)
def search_state(name_keyword: Optional[str] = None) -> str:
    """
    查询任务状态。如果不提供关键字，则返回所有状态。
    """

    trace("UseTool", "SearchState", name_keyword, level="info")
    trace("SearchState", "Input", f"name_keyword: {name_keyword}", level="debug")

    states = state_service.get_all_states()
    if name_keyword:
        states = [s for s in states if name_keyword.lower() in s["state_name"].lower()]

    if not states:
        return "未找到任何匹配的任务状态。"

    lines = [f"找到 {len(states)} 个状态："]
    for s in states:
        lines.append(f"ID {s['id']}: {s['state_name']} (颜色: {s['state_color']})")
    return "\n".join(lines)