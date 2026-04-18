import streamlit as st
import streamlit_antd_components as sac

from pages.subPages.tasks.showTasks import todayTasks, overview
from pages.subPages.widgets.navbar import navbar

st.set_page_config(page_title="Task Scheduler", layout="wide")

PAGENAME = "app"

with st.sidebar:
    navbar(PAGENAME)

# ==================================
# 页面内容区
# ==================================

col_mainT, col_subT = st.columns([1,2])

with col_subT:
    st.title("Task Scheduler",text_alignment="right")

with col_mainT:
    st.title("看板")

col_today, col_blank, col_overview = st.columns([15,1,20])

with col_today:
    todayTasks()
with col_overview:
    overview()