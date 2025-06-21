import streamlit as st
import requests
import os

# API地址，指向后端公网地址
API_BASE_URL = "https://uce-accounting-rag-bpadevgmg4bkbqeg.canadaeast-01.azurewebsites.net/api"

st.set_page_config(
    page_title="RAG应收帐系统",
    page_icon="💰",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "file_status" not in st.session_state:
    st.session_state.file_status = "未上传"
if "api_status" not in st.session_state:
    st.session_state.api_status = "未连接"

def upload_file(file) -> bool:
    try:
        files = {"file": file}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        if response.status_code == 200:
            data = response.json()
            st.session_state.file_status = f"已上传（公司数: {data['total_companies']}，总金额: {data['total_amount']:,.2f}）"
            return True
        else:
            st.session_state.file_status = f"上传失败: {response.json()['detail']}"
            return False
    except Exception as e:
        st.session_state.file_status = f"上传出错: {str(e)}"
        return False

def send_query(query: str) -> str:
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"query": query}
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"查询失败: {response.json()['detail']}"
    except Exception as e:
        return f"查询出错: {str(e)}"

def check_api_status():
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            st.session_state.api_status = "已连接"
        else:
            st.session_state.api_status = "连接异常"
    except Exception:
        st.session_state.api_status = "未连接"

check_api_status()

with st.sidebar:
    st.markdown("---")
    st.subheader("上传Excel文件")
    uploaded_file = st.file_uploader("选择AR_data.xlsx文件", type=["xlsx"])
    if uploaded_file and not st.session_state.file_uploaded:
        if upload_file(uploaded_file):
            st.session_state.file_uploaded = True
    st.info(f"文件状态: {st.session_state.file_status}")
    st.info(f"API状态: {st.session_state.api_status}")
    st.markdown("---")
    with st.expander("使用说明", expanded=False):
        st.markdown("""
        1. **上传AR_data.xlsx文件**
        2. 在主界面输入您的问题，例如：
           - "显示所有逾期超过60天的公司"
           - "哪家公司的应收账款最多？"
           - "分析某公司的付款情况"
        3. 聊天记录仅本地保存，不会上传服务器。
        """)

st.header("RAG应收帐系统 💰")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
if prompt := st.chat_input("请输入您的问题..."):
    if not st.session_state.file_uploaded:
        st.error("请先在左侧上传Excel文件！")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = send_query(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response}) 