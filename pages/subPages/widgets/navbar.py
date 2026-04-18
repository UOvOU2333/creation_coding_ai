import streamlit as st

# ==============================
# 页面间跳转（顶端导航栏）
# ==============================

def navbar(pageName):

    with st.expander("页面导航栏"):
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("首页", key=f"btn_home_{pageName}", use_container_width=True, type="primary"):
                st.switch_page("app.py")
        with col_nav2:
            if st.button("任务管理", key=f"btn_task_{pageName}", use_container_width=True):
                st.switch_page("pages/managingPage.py")
    
    if pageName == "app":

        # 初始化会话状态
        if "messages" not in st.session_state:
            st.session_state.messages = []  # 存储 {"role": "user/assistant", "content": str}
        if "intermediate_steps" not in st.session_state:
            st.session_state.intermediate_steps = []

        # 清空历史对话按钮放在标题旁边
        if st.button("🗑️ 清空历史对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.intermediate_steps = []
            st.rerun()

        # Agent 执行步骤（折叠区域）
        with st.expander("🔧 查看 Agent 执行步骤"):
            if st.session_state.intermediate_steps:
                for step in st.session_state.intermediate_steps:
                    st.text(step)
            else:
                st.info("暂无执行步骤，发送消息后会显示。")
