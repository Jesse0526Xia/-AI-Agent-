"""
工具注册中心
管理所有可用工具
"""

from typing import List, Dict, Optional
from loguru import logger

from .base_tool import Tool
from .search_tool import WebSearchTool, FileSearchTool
from .file_tool import ReadFileTool, WriteFileTool
from .code_tool import ExecuteCodeTool
from .data_tool import AnalyzeDataTool


class ToolRegistry:
    """工具注册中心"""
    
    _tools: Dict[str, Tool] = {}
    
    @classmethod
    def register(cls, tool: Tool):
        """
        注册工具
        
        Args:
            tool: 工具实例
        """
        cls._tools[tool.name] = tool
        logger.info(f"注册工具: {tool.name}")
    
    @classmethod
    def unregister(cls, tool_name: str):
        """
        注销工具
        
        Args:
            tool_name: 工具名称
        """
        if tool_name in cls._tools:
            del cls._tools[tool_name]
            logger.info(f"注销工具: {tool_name}")
    
    @classmethod
    def get(cls, tool_name: str) -> Optional[Tool]:
        """
        获取工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例
        """
        return cls._tools.get(tool_name)
    
    @classmethod
    def get_all(cls) -> List[Tool]:
        """
        获取所有工具
        
        Returns:
            工具列表
        """
        return list(cls._tools.values())
    
    @classmethod
    def get_all_names(cls) -> List[str]:
        """
        获取所有工具名称
        
        Returns:
            工具名称列表
        """
        return list(cls._tools.keys())
    
    @classmethod
    def get_tools_description(cls) -> str:
        """
        获取所有工具的描述
        
        Returns:
            工具描述字符串
        """
        descriptions = []
        for name, tool in cls._tools.items():
            desc = f"- {name}: {tool.description}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    @classmethod
    def initialize_default_tools(cls):
        """初始化默认工具集"""
        # 搜索工具
        cls.register(WebSearchTool())
        cls.register(FileSearchTool())
        
        # 文件工具
        cls.register(ReadFileTool())
        cls.register(WriteFileTool())
        
        # 代码执行工具
        cls.register(ExecuteCodeTool())
        
        # 数据分析工具
        cls.register(AnalyzeDataTool())
        
        logger.info(f"默认工具初始化完成，共 {len(cls._tools)} 个工具")
    
    @classmethod
    def clear(cls):
        """清空所有工具"""
        cls._tools.clear()
        logger.info("所有工具已清空")
