"""
数据分析工具
提供数据分析和可视化功能
"""

from typing import Dict, Any
from pathlib import Path

from .base_tool import Tool


class AnalyzeDataTool(Tool):
    """数据分析工具"""
    
    name = "analyze_data"
    description = "分析数据文件，支持统计分析、趋势分析等"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "数据文件路径"
            },
            "analysis_type": {
                "type": "string",
                "description": "分析类型",
                "enum": ["summary", "describe", "correlation", "trend"],
                "default": "summary"
            }
        },
        "required": ["file_path"]
    }
    
    def run(
        self,
        file_path: str,
        analysis_type: str = "summary"
    ) -> str:
        """
        分析数据
        
        Args:
            file_path: 数据文件路径
            analysis_type: 分析类型
            
        Returns:
            分析结果
        """
        try:
            import pandas as pd
            import numpy as np
            
            # 读取数据
            path = Path(file_path)
            suffix = path.suffix.lower()
            
            if suffix == ".csv":
                df = pd.read_csv(file_path)
            elif suffix in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                return f"不支持的文件格式: {suffix}"
            
            # 执行分析
            if analysis_type == "summary":
                result = self._summary_analysis(df)
            elif analysis_type == "describe":
                result = self._describe_analysis(df)
            elif analysis_type == "correlation":
                result = self._correlation_analysis(df)
            elif analysis_type == "trend":
                result = self._trend_analysis(df)
            else:
                result = self._summary_analysis(df)
            
            return result
        
        except ImportError:
            return "数据分析需要安装pandas和numpy库"
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def _summary_analysis(self, df) -> str:
        """摘要分析"""
        result = []
        result.append(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        result.append(f"\n列名: {list(df.columns)}")
        result.append(f"\n数据类型:\n{df.dtypes}")
        result.append(f"\n缺失值统计:\n{df.isnull().sum()}")
        result.append(f"\n前5行数据:\n{df.head()}")
        
        return "\n".join(result)
    
    def _describe_analysis(self, df) -> str:
        """描述性统计分析"""
        result = []
        result.append("数值列统计:")
        result.append(str(df.describe()))
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            result.append("\n分类列统计:")
            for col in categorical_cols:
                result.append(f"\n{col}:")
                result.append(str(df[col].value_counts().head(10)))
        
        return "\n".join(result)
    
    def _correlation_analysis(self, df) -> str:
        """相关性分析"""
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.shape[1] < 2:
            return "数值列少于2个，无法进行相关性分析"
        
        corr = numeric_df.corr()
        return f"相关系数矩阵:\n{corr}"
    
    def _trend_analysis(self, df) -> str:
        """趋势分析"""
        result = []
        
        # 简单的趋势分析
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols[:5]:  # 最多分析5列
            values = df[col].dropna()
            if len(values) > 1:
                # 计算趋势
                trend = "上升" if values.iloc[-1] > values.iloc[0] else "下降"
                change = (values.iloc[-1] - values.iloc[0]) / values.iloc[0] * 100
                
                result.append(f"{col}: {trend} ({change:.2f}%)")
        
        return "\n".join(result)


class CreateChartTool(Tool):
    """创建图表工具"""
    
    name = "create_chart"
    description = "根据数据创建可视化图表"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "数据文件路径"
            },
            "chart_type": {
                "type": "string",
                "description": "图表类型",
                "enum": ["line", "bar", "pie", "scatter", "histogram"],
                "default": "line"
            },
            "x_column": {
                "type": "string",
                "description": "X轴列名"
            },
            "y_column": {
                "type": "string",
                "description": "Y轴列名"
            },
            "output_path": {
                "type": "string",
                "description": "输出图片路径",
                "default": "chart.png"
            }
        },
        "required": ["file_path"]
    }
    
    def run(
        self,
        file_path: str,
        chart_type: str = "line",
        x_column: str = None,
        y_column: str = None,
        output_path: str = "chart.png"
    ) -> str:
        """
        创建图表
        
        Args:
            file_path: 数据文件路径
            chart_type: 图表类型
            x_column: X轴列名
            y_column: Y轴列名
            output_path: 输出路径
            
        Returns:
            操作结果
        """
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            # 读取数据
            df = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            
            if chart_type == "line":
                if x_column and y_column:
                    plt.plot(df[x_column], df[y_column])
                else:
                    df.plot()
            elif chart_type == "bar":
                if x_column and y_column:
                    plt.bar(df[x_column], df[y_column])
                else:
                    df.plot(kind='bar')
            elif chart_type == "pie":
                if y_column:
                    df[y_column].value_counts().plot(kind='pie')
            elif chart_type == "scatter":
                if x_column and y_column:
                    plt.scatter(df[x_column], df[y_column])
            elif chart_type == "histogram":
                if y_column:
                    plt.hist(df[y_column], bins=30)
            
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
            return f"图表已保存到: {output_path}"
        
        except Exception as e:
            return f"创建图表失败: {str(e)}"
