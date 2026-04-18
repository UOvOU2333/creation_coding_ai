from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from services import type_service\

from chains.agent import trace


class SearchTypeInput(BaseModel):
    name_keyword: Optional[str] = Field(default=None, description="类型名称模糊匹配关键字")


@tool(args_schema=SearchTypeInput)
def search_type(name_keyword: Optional[str] = None) -> str:
    """
    查询任务类型。如果不提供关键字，则返回所有类型。
    """

    trace("UseTool", "SearchType", name_keyword, level="info")
    trace("SearchType", "name_keyword", name_keyword, level="debug")

    types = type_service.get_all_types()
    if name_keyword:
        types = [t for t in types if name_keyword.lower() in t["type_name"].lower()]

    if not types:
        return "未找到任何匹配的任务类型。"

    lines = [f"找到 {len(types)} 个类型："]
    for t in types:
        lines.append(f"ID {t['id']}: {t['type_name']} (颜色: {t['type_color']})")
    return "\n".join(lines)