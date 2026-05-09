"""
工具基类
定义工具的标准接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """工具参数定义"""
    type: str
    description: Optional[str] = None
    enum: Optional[list] = None
    default: Optional[Any] = None


class Tool(ABC):
    """工具基类"""
    
    name: str = "base_tool"
    description: str = "基础工具"
    parameters: Dict[str, Any] = {}
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            执行结果
        """
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        验证参数
        
        Args:
            **kwargs: 待验证的参数
            
        Returns:
            是否有效
        """
        if not self.parameters:
            return True
        
        required = self.parameters.get("required", [])
        properties = self.parameters.get("properties", {})
        
        # 检查必需参数
        for param in required:
            if param not in kwargs:
                return False
        
        # 检查参数类型（简化版）
        for key, value in kwargs.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    return False
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    return False
                elif expected_type == "boolean" and not isinstance(value, bool):
                    return False
                elif expected_type == "array" and not isinstance(value, list):
                    return False
                elif expected_type == "object" and not isinstance(value, dict):
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            工具信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def __repr__(self) -> str:
        return f"Tool(name={self.name}, description={self.description})"
