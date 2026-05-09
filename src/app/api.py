"""
FastAPI接口
提供RESTful API服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from loguru import logger

from ..agent.react_agent import ReActAgent
from ..tools.tool_registry import ToolRegistry
from ..memory.short_term import ShortTermMemory
from ..llm.llm_client import LLMClient


# 请求模型
class TaskRequest(BaseModel):
    """任务请求"""
    task: str
    max_iterations: Optional[int] = 15
    verbose: Optional[bool] = False


class TaskResponse(BaseModel):
    """任务响应"""
    task: str
    result: str
    success: bool
    iterations: Optional[int] = None


# 创建FastAPI应用
app = FastAPI(
    title="AI Agent智能助手API",
    description="基于ReAct框架的智能Agent系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Agent实例
agent: ReActAgent = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global agent
    
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
    
    logger.info("API服务启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    logger.info("API服务关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Agent智能助手API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """
    执行任务
    
    Args:
        request: 任务请求
        
    Returns:
        任务响应
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    try:
        # 执行任务
        result = agent.run(request.task)
        
        return TaskResponse(
            task=request.task,
            result=result,
            success=True
        )
    
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        return TaskResponse(
            task=request.task,
            result=str(e),
            success=False
        )


@app.get("/tools")
async def list_tools():
    """列出所有可用工具"""
    tools = ToolRegistry.get_all()
    
    return {
        "tools": [tool.to_dict() for tool in tools],
        "count": len(tools)
    }


@app.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    """获取工具详情"""
    tool = ToolRegistry.get(tool_name)
    
    if tool is None:
        raise HTTPException(status_code=404, detail=f"工具不存在: {tool_name}")
    
    return tool.to_dict()


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agent": "initialized" if agent else "not_initialized"
    }


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """运行API服务"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()
