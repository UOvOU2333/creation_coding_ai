import streamlit as st
import warnings
import logging

# 抑制 transformers 的警告和错误（如果未安装 torchvision）
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

from chains.agent import build_agent
from langchain_core.messages import HumanMessage, AIMessage

# 不再设置页面配置，由父页面统一控制
def agent():
    st.caption("我可以帮你创建、查询、更新任务，以及管理任务类型和状态。")

    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = []  # 存储 {"role": "user/assistant", "content": str}
    if "agent" not in st.session_state:
        with st.spinner("正在初始化 Agent ..."):
            st.session_state.agent = build_agent()
    if "intermediate_steps" not in st.session_state:
        st.session_state.intermediate_steps = []

    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 用户输入
    if prompt := st.chat_input("我可以帮你创建、查询、更新任务，以及管理任务类型和状态。例如：帮我创建一个明天交报告的任务，优先级高"):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 构建 LangChain 格式的聊天历史（用于多轮对话）
        chat_history = []
        for msg in st.session_state.messages[:-1]:  # 不包括当前消息
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            else:
                chat_history.append(AIMessage(content=msg["content"]))

        # 调用 Agent
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    response = st.session_state.agent.invoke(
                        {
                            "input": prompt,
                            "chat_history": chat_history,
                            "agent_scratchpad": []
                        }
                    )
                    output = response.get("output", "抱歉，我无法处理这个请求。")
                    steps = response.get("intermediate_steps", [])

                    # 记录中间步骤
                    step_texts = []
                    for action, observation in steps:
                        tool_name = action.tool
                        tool_input = action.tool_input
                        step_texts.append(f"🔨 调用工具: {tool_name}\n   输入: {tool_input}\n   输出: {observation}")
                    st.session_state.intermediate_steps = step_texts

                    st.markdown(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                except Exception as e:
                    error_msg = f"❌ 发生错误: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.session_state.intermediate_steps = [f"错误: {str(e)}"]

        st.rerun()