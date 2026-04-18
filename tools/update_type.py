from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from services import type_service

from chains.loger import trace


class UpdateTypeInput(BaseModel):
    type_id: int = Field(description="要更新的类型ID")
    type_name: Optional[str] = Field(default=None, description="新的类型名称")
    type_color: Optional[str] = Field(default=None, description="新的颜色代码")


@tool(args_schema=UpdateTypeInput)
def update_type(type_id: int, type_name: Optional[str] = None, type_color: Optional[str] = None) -> str:
    """
    更新任务类型的名称或颜色。
    """

    trace("UseTool", "UpdateType", type_name, level="info")
    trace("UpdateType", "type_id, type_name, type_color", f"{type_id}, {type_name}, {type_color}", level="debug")

    # 检查类型是否存在
    types = type_service.get_all_types()
    existing = None
    for t in types:
        if t["id"] == type_id:
            existing = t
            break
    if existing is None:
        return f"错误：未找到 ID 为 {type_id} 的类型。"

    # 使用现有值作为默认值
    new_name = type_name if type_name is not None else existing["type_name"]
    new_color = type_color if type_color is not None else existing["type_color"]

    try:
        type_service.update_type(type_id, new_name, new_color)
        return f"类型 ID {type_id} 更新成功。"
    except Exception as e:
        return f"更新类型时出错：{str(e)}"