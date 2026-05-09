"""
Streamlit交互界面
提供用户友好的Agent交互界面
"""

import streamlit as st
from typing import List, Dict
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agent.react_agent import ReActAgent
from src.tools.tool_registry import ToolRegistry
from src.memory.short_term import ShortTermMemory
from src.llm.llm_client import LLMClient
from loguru import logger


def init_agent():
    """初始化Agent"""
    # 初始化工具
    ToolRegistry.initialize_default_tools()
    tools = ToolRegistry.get_all()
    
    # 初始化LLM
    llm = LLMClient(
        provider="openai",
        model="gpt-4-turbo-preview"
    )
    
    # 初始化记忆
    memory = ShortTermMemory()
    
    # 创建Agent
    agent = ReActAgent(
        llm=llm,
        tools=tools,
        memory=memory,
        verbose=True
    )
    
    return agent


def main():
    """主函数"""
    st.set_page_config(
        page_title="AI Agent智能助手",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Agent智能助手")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("系统设置")
        
        # Agent配置
        st.subheader("Agent配置")
        max_iterations = st.slider("最大迭代次数", 5, 30, 15)
        verbose = st.checkbox("显示详细过程", value=True)
        
        st.markdown("---")
        
        # 工具管理
        st.subheader("可用工具")
        tools = ToolRegistry.get_all_names()
        for tool in tools:
            st.text(f"• {tool}")
        
        st.markdown("---")
        
        # 对话管理
        st.subheader("对话管理")
        if st.button("清空对话历史"):
            st.session_state.messages = []
            st.success("对话历史已清空")
        
        if st.button("导出对话"):
            # 导出对话历史
            pass
    
    # 主界面
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("请输入您的任务"):
        # 显示用户消息
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Agent执行
        with st.chat_message("assistant"):
            with st.spinner("Agent正在思考和执行..."):
                # 这里应该调用Agent
                # 简化示例
                result = f"这是一个示例响应。您的任务是：{prompt}"
                
                # 显示执行过程
                with st.expander("查看执行过程"):
                    st.code("Thought: 分析任务...\nAction: search_web\nObservation: 找到相关信息...")
                
                st.markdown(result)
                
                # 保存到对话历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result
                })


if __name__ == "__main__":
    main()
