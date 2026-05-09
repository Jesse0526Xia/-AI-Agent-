"""
搜索工具
包括网络搜索和文件搜索
"""

from typing import Dict, Any, List
from pathlib import Path
import os

from .base_tool import Tool


class WebSearchTool(Tool):
    """网络搜索工具"""
    
    name = "search_web"
    description = "在网络上搜索信息，返回相关结果"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询词"
            },
            "num_results": {
                "type": "number",
                "description": "返回结果数量",
                "default": 5
            }
        },
        "required": ["query"]
    }
    
    def run(self, query: str, num_results: int = 5) -> str:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询词
            num_results: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
            
            if not results:
                return "未找到相关结果"
            
            # 格式化结果
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   链接: {result['href']}\n"
                    f"   摘要: {result['body'][:200]}..."
                )
            
            return "\n\n".join(formatted_results)
        
        except Exception as e:
            return f"搜索失败: {str(e)}"


class FileSearchTool(Tool):
    """文件搜索工具"""
    
    name = "search_files"
    description = "在指定目录中搜索文件"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "文件名模式（支持通配符）"
            },
            "directory": {
                "type": "string",
                "description": "搜索目录",
                "default": "."
            },
            "recursive": {
                "type": "boolean",
                "description": "是否递归搜索",
                "default": True
            }
        },
        "required": ["pattern"]
    }
    
    def run(
        self,
        pattern: str,
        directory: str = ".",
        recursive: bool = True
    ) -> str:
        """
        执行文件搜索
        
        Args:
            pattern: 文件名模式
            directory: 搜索目录
            recursive: 是否递归搜索
            
        Returns:
            搜索结果
        """
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return f"目录不存在: {directory}"
            
            # 搜索文件
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
            
            if not files:
                return f"未找到匹配的文件: {pattern}"
            
            # 格式化结果
            formatted_results = []
            for i, file_path in enumerate(files[:20], 1):  # 最多显示20个
                file_info = os.stat(file_path)
                formatted_results.append(
                    f"{i}. {file_path}\n"
                    f"   大小: {file_info.st_size} 字节\n"
                    f"   修改时间: {file_info.st_mtime}"
                )
            
            if len(files) > 20:
                formatted_results.append(f"\n... 还有 {len(files) - 20} 个文件")
            
            return "\n\n".join(formatted_results)
        
        except Exception as e:
            return f"搜索失败: {str(e)}"
