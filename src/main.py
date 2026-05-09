"""
主入口文件
"""

import argparse
from loguru import logger

from .app.api import run_api


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Agent智能助手")
    parser.add_argument(
        "--mode",
        type=str,
        default="api",
        choices=["api", "streamlit", "cli"],
        help="运行模式: api, streamlit 或 cli"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="API服务地址"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API服务端口"
    )
    
    args = parser.parse_args()
    
    logger.info(f"启动模式: {args.mode}")
    
    if args.mode == "api":
        # 启动API服务
        run_api(host=args.host, port=args.port)
    
    elif args.mode == "streamlit":
        # 启动Streamlit
        logger.info("请使用以下命令启动Streamlit:")
        logger.info("streamlit run src/app/streamlit_app.py")
    
    elif args.mode == "cli":
        # 命令行交互模式
        run_cli()


def run_cli():
    """命令行交互模式"""
    from .agent.react_agent import ReActAgent
    from .tools.tool_registry import ToolRegistry
    from .memory.short_term import ShortTermMemory
    from .llm.llm_client import LLMClient
    
    print("=" * 50)
    print("AI Agent智能助手 - 命令行模式")
    print("=" * 50)
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'clear' 清空对话历史")
    print("=" * 50)
    
    # 初始化
    ToolRegistry.initialize_default_tools()
    tools = ToolRegistry.get_all()
    
    llm = LLMClient(
        provider="openai",
        model="gpt-4-turbo-preview"
    )
    
    memory = ShortTermMemory()
    
    agent = ReActAgent(
        llm=llm,
        tools=tools,
        memory=memory,
        verbose=True
    )
    
    # 交互循环
    while True:
        try:
            task = input("\n请输入任务: ").strip()
            
            if not task:
                continue
            
            if task.lower() in ["quit", "exit"]:
                print("再见！")
                break
            
            if task.lower() == "clear":
                memory.clear()
                print("对话历史已清空")
                continue
            
            # 执行任务
            print("\n" + "=" * 50)
            result = agent.run(task)
            print("=" * 50)
            print(f"\n结果: {result}")
        
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
