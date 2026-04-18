from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.add_task import add_task
from tools.add_type import add_type
# (Banned) from tools.delete_task import delete_task
from tools.search_state import search_state
from tools.search_task import search_task
from tools.search_type import search_type
from tools.update_state import update_state
from tools.update_task import update_task
from tools.update_type import update_type

from chains.prompt import SYSTEM_PROMPT

import os
from dotenv import load_dotenv
from datetime import datetime   # 修正导入

def build_agent():
    load_dotenv()

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0,
        max_retries=3,
        streaming=False,
        request_timeout=120
    )

    tools = [
        add_task,
        add_type,
        # (Banned) delete_task,
        search_state,
        search_task,
        search_type,
        update_state,
        update_task,
        update_type
    ]

    # 修正日期获取
    current_date = datetime.now().date().isoformat()
    system_prompt_with_date = SYSTEM_PROMPT.replace("今天是 **2026-04-18**", f"今天是 **{current_date}**")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_with_date),
        MessagesPlaceholder(variable_name="chat_history", optional=True),  # 支持多轮对话
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        return_intermediate_steps=True   # 关键修复
    )

    return executor