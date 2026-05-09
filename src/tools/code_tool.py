"""
代码执行工具
在沙箱环境中执行Python代码
"""

from typing import Dict, Any
import subprocess
import tempfile
import os

from .base_tool import Tool


class ExecuteCodeTool(Tool):
    """代码执行工具"""
    
    name = "execute_code"
    description = "执行Python代码并返回结果"
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "要执行的Python代码"
            },
            "timeout": {
                "type": "number",
                "description": "执行超时时间（秒）",
                "default": 60
            }
        },
        "required": ["code"]
    }
    
    def run(self, code: str, timeout: int = 60) -> str:
        """
        执行Python代码
        
        Args:
            code: Python代码
            timeout: 超时时间
            
        Returns:
            执行结果
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            # 执行代码
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="data/workspace"  # 工作目录
            )
            
            # 删除临时文件
            os.unlink(temp_file)
            
            # 返回结果
            if result.returncode == 0:
                output = result.stdout
                if not output:
                    output = "代码执行成功，无输出"
                return output
            else:
                return f"执行失败:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            return f"执行超时（超过 {timeout} 秒）"
        except Exception as e:
            return f"执行失败: {str(e)}"


class SafeExecuteCodeTool(Tool):
    """安全的代码执行工具（使用RestrictedPython）"""
    
    name = "safe_execute_code"
    description = "在受限环境中安全执行Python代码"
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "要执行的Python代码"
            }
        },
        "required": ["code"]
    }
    
    def run(self, code: str) -> str:
        """
        安全执行Python代码
        
        Args:
            code: Python代码
            
        Returns:
            执行结果
        """
        try:
            from RestrictedPython import compile_restricted
            from RestrictedPython.Guards import safe_builtins
            
            # 编译代码
            byte_code = compile_restricted(
                code,
                filename="<inline>",
                mode="exec"
            )
            
            # 准备执行环境
            restricted_globals = {
                "__builtins__": safe_builtins,
                "_print_": lambda x: x,  # 允许print
            }
            restricted_locals = {}
            
            # 执行代码
            exec(byte_code, restricted_globals, restricted_locals)
            
            # 获取结果
            if "result" in restricted_locals:
                return str(restricted_locals["result"])
            else:
                return "代码执行成功"
        
        except SyntaxError as e:
            return f"语法错误: {str(e)}"
        except Exception as e:
            return f"执行失败: {str(e)}"
