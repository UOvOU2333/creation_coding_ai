from langchain_core.tools import tool
from pydantic import BaseModel, Field
from services import type_service

from chains.loger import trace


class AddTypeInput(BaseModel):
    type_name: str = Field(description="新的任务类型名称，必须唯一")
    type_color: str = Field(description="颜色代码，例如 #3b82f6 或 red")


@tool(args_schema=AddTypeInput)
def add_type(type_name: str, type_color: str) -> str:
    """
    添加一个新的任务类型。
    """

    trace("UseTool", "AddType", type_name, level="info")
    trace("AddType", "Input", f"type_name: {type_name}, type_color: {type_color}", level="debug")

    # 可选：检查是否已存在同名类型
    existing = type_service.get_all_types()
    for t in existing:
        if t["type_name"] == type_name:
            return f"错误：类型 '{type_name}' 已存在。"

    try:
        type_service.add_type(type_name, type_color)
        return f"任务类型 '{type_name}' 添加成功。"
    except Exception as e:
        return f"添加类型时出错：{str(e)}"