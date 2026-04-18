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
import logging

LOG_PATH = os.path.join(os.path.dirname(__file__), "agent_execution.log")

logging.basicConfig(
    level=logging.DEBUG,  # 记录 INFO 及以上级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
    ]
)

def trace(titile: str, header: str, content: str, level: str = "info"):
    getattr(logging, level)(f"[{titile}] {header} --> {content}")

def build_agent():
    load_dotenv()

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0,
        max_retries=3,
        streaming=False,          # 禁用流式
        request_timeout=120
    )

    tools = [
        add_task,
        add_type,
        # delete_task,   # 禁用，避免误删
        search_state,
        search_task,
        search_type,
        update_state,
        update_task,
        update_type
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),   # 这一行必须加
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
        max_iterations=10
    )

    return executor