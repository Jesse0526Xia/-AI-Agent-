# 多工具协同AI Agent智能助手

基于ReAct框架构建的智能Agent系统，支持多工具协同调用、任务自动规划与执行。

## 项目特点

- **ReAct框架**：推理-行动循环，自主理解任务并执行
- **多工具协同**：10+工具（搜索、代码执行、数据分析、文件操作等）
- **任务规划**：自动分解复杂任务为子任务
- **反思纠错**：执行失败时自动重试或选择替代方案
- **双层记忆**：短期对话记忆 + 长期向量记忆
- **安全隔离**：沙箱环境执行代码

## 技术栈

- **Agent框架**: LangChain Agent
- **LLM**: GPT-4, Claude, 通义千问
- **工具执行**: Python沙箱环境
- **记忆存储**: Redis + Milvus
- **Web框架**: FastAPI + Streamlit
- **数据处理**: Pandas, NumPy

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp config/config.yaml.example config/config.yaml
```

修改配置文件，填入你的API密钥。

### 3. 启动服务

启动API服务：
```bash
python src/main.py --mode api
```

启动Streamlit界面：
```bash
streamlit run src/app/streamlit_app.py
```

## 项目结构

```
ai-agent-assistant/
├── config/              # 配置文件
│   └── prompts/        # Prompt模板
├── src/
│   ├── agent/          # Agent核心（ReAct、规划器、反思器）
│   ├── tools/          # 工具集
│   ├── memory/         # 记忆系统
│   ├── llm/            # LLM客户端
│   ├── app/            # 应用层（API、界面）
│   └── utils/          # 工具函数
├── tests/              # 测试代码
├── data/               # 数据目录
└── docs/               # 文档
```

## 核心功能

### 使用Agent执行任务

```python
from src.agent.react_agent import ReActAgent
from src.tools.tool_registry import ToolRegistry

# 初始化工具
tools = ToolRegistry.get_all_tools()

# 创建Agent
agent = ReActAgent(tools=tools)

# 执行任务
result = agent.run("分析sales.csv文件，生成销售报告")
print(result)
```

### 添加自定义工具

```python
from src.tools.base_tool import Tool

class MyCustomTool(Tool):
    name = "my_tool"
    description = "我的自定义工具"
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        },
        "required": ["input"]
    }
    
    def run(self, input: str):
        # 实现工具逻辑
        return f"处理结果: {input}"

# 注册工具
ToolRegistry.register(MyCustomTool())
```

## 内置工具

| 工具名称 | 功能描述 |
|---------|---------|
| search_web | 网络搜索 |
| search_files | 文件搜索 |
| read_file | 读取文件 |
| write_file | 写入文件 |
| execute_code | 执行Python代码 |
| analyze_data | 数据分析 |
| query_database | 数据库查询 |
| call_api | API调用 |
| send_email | 发送邮件 |
