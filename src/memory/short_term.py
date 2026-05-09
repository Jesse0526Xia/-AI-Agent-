"""
记忆系统
包括短期记忆和长期记忆
"""

from typing import List, Dict, Any
from loguru import logger


class ShortTermMemory:
    """短期记忆 - 存储当前对话的上下文"""
    
    def __init__(self, max_history: int = 10, max_tokens: int = 4000):
        """
        初始化短期记忆
        
        Args:
            max_history: 最大对话历史轮数
            max_tokens: 最大token数
        """
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.history: List[Dict[str, str]] = []
        
        logger.info(f"短期记忆初始化完成，最大历史: {max_history} 轮")
    
    def add_message(self, role: str, content: str):
        """
        添加消息
        
        Args:
            role: 角色 (user/assistant)
            content: 消息内容
        """
        self.history.append({
            "role": role,
            "content": content
        })
        
        # 保持历史记录在限制范围内
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history*2:]
        
        logger.debug(f"添加消息: {role} - {content[:50]}...")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.history
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """
        获取最近N条消息
        
        Args:
            n: 消息数量
            
        Returns:
            消息列表
        """
        return self.history[-n*2:] if n > 0 else []
    
    def clear(self):
        """清空记忆"""
        self.history = []
        logger.info("短期记忆已清空")
    
    def get_context_string(self) -> str:
        """
        获取上下文字符串
        
        Returns:
            格式化的上下文字符串
        """
        context = []
        for msg in self.history:
            role = "用户" if msg["role"] == "user" else "助手"
            context.append(f"{role}: {msg['content']}")
        return "\n".join(context)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            记忆字典
        """
        return {
            "history": self.history,
            "max_history": self.max_history,
            "max_tokens": self.max_tokens
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShortTermMemory":
        """
        从字典创建
        
        Args:
            data: 字典数据
            
        Returns:
            短期记忆实例
        """
        memory = cls(
            max_history=data.get("max_history", 10),
            max_tokens=data.get("max_tokens", 4000)
        )
        memory.history = data.get("history", [])
        return memory
