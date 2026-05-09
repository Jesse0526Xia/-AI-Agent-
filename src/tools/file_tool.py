"""
文件操作工具
包括读取和写入文件
"""

from typing import Dict, Any
from pathlib import Path

from .base_tool import Tool


class ReadFileTool(Tool):
    """读取文件工具"""
    
    name = "read_file"
    description = "读取文件内容"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文件路径"
            },
            "encoding": {
                "type": "string",
                "description": "文件编码",
                "default": "utf-8"
            }
        },
        "required": ["file_path"]
    }
    
    def run(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        读取文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            文件内容
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return f"文件不存在: {file_path}"
            
            # 检查文件大小
            file_size = path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB
                return f"文件过大 ({file_size} 字节)，请使用专门的工具处理"
            
            # 根据文件类型读取
            suffix = path.suffix.lower()
            
            if suffix == ".pdf":
                return self._read_pdf(path)
            elif suffix == ".docx":
                return self._read_docx(path)
            elif suffix == ".xlsx":
                return self._read_xlsx(path)
            else:
                # 默认作为文本文件读取
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()
                return content
        
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    def _read_pdf(self, path: Path) -> str:
        """读取PDF文件"""
        try:
            import PyPDF2
            
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except:
            return "PDF读取需要安装PyPDF2库"
    
    def _read_docx(self, path: Path) -> str:
        """读取Word文件"""
        try:
            from docx import Document
            
            doc = Document(path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except:
            return "Word读取需要安装python-docx库"
    
    def _read_xlsx(self, path: Path) -> str:
        """读取Excel文件"""
        try:
            import pandas as pd
            
            df = pd.read_excel(path)
            return df.to_string()
        except:
            return "Excel读取需要安装pandas和openpyxl库"


class WriteFileTool(Tool):
    """写入文件工具"""
    
    name = "write_file"
    description = "将内容写入文件"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "要写入的内容"
            },
            "mode": {
                "type": "string",
                "description": "写入模式: write或append",
                "enum": ["write", "append"],
                "default": "write"
            }
        },
        "required": ["file_path", "content"]
    }
    
    def run(
        self,
        file_path: str,
        content: str,
        mode: str = "write"
    ) -> str:
        """
        写入文件
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            mode: 写入模式
            
        Returns:
            操作结果
        """
        try:
            path = Path(file_path)
            
            # 创建父目录
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            write_mode = "w" if mode == "write" else "a"
            with open(path, write_mode, encoding="utf-8") as f:
                f.write(content)
            
            return f"成功写入文件: {file_path} ({len(content)} 字符)"
        
        except Exception as e:
            return f"写入文件失败: {str(e)}"
