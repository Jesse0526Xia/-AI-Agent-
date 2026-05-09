"""
LLM客户端
封装大语言模型调用
"""

from typing import Optional, Dict, Any, List
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4-turbo-preview",
        api_key: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化LLM客户端
        
        Args:
            provider: 提供商 (openai, claude, qwen)
            model: 模型名称
            api_key: API密钥
            temperature: 生成温度
            max_tokens: 最大token数
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 初始化LLM
        if provider == "openai":
            self.llm = ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # 其他提供商的实现
            raise NotImplementedError(f"不支持的提供商: {provider}")
        
        logger.info(f"LLM客户端初始化完成: {provider}/{model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            temperature: 生成温度
            
        Returns:
            生成的文本
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        # 设置温度
        temp = temperature if temperature is not None else self.temperature
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def generate_with_history(
        self,
        prompt: str,
        history: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        带历史记录的生成
        
        Args:
            prompt: 提示词
            history: 对话历史
            system_prompt: 系统提示词
            
        Returns:
            生成的文本
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        # 添加历史记录
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # 添加当前提示
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ):
        """
        流式生成
        
        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            
        Yields:
            生成的文本片段
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        try:
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"LLM流式调用失败: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        计算token数量
        
        Args:
            text: 文本
            
        Returns:
            token数量
        """
        # 简化实现，实际应使用tiktoken
        return len(text) // 4  # 粗略估计
