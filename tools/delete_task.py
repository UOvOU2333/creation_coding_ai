from langchain_core.tools import tool
from pydantic import BaseModel, Field
from services import task_service

from chains.loger import trace


class DeleteTaskInput(BaseModel):
    task_id: int = Field(description="要删除的任务ID")


@tool(args_schema=DeleteTaskInput)
def delete_task(task_id: int) -> str:
    """
    根据任务ID删除任务（硬删除）。注意：这会同时删除关联的评论（因外键级联删除）。
    """

    trace("UseTool", "DeleteTask", task_id, level="info")
    trace("DeleteTask", "Input", f"task_id: {task_id}", level="debug")

    # 先检查任务是否存在
    task = task_service.get_task_by_id(task_id)
    if task is None:
        return f"错误：未找到 ID 为 {task_id} 的任务。"

    try:
        task_service.delete_task(task_id)
        return f"任务 ID {task_id} 已成功删除。"
    except Exception as e:
        return f"删除任务时出错：{str(e)}"