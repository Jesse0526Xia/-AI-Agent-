"""
ReAct Agent核心实现
基于推理-行动循环的智能Agent
"""

from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import re

from ..llm.llm_client import LLMClient
from ..memory.short_term import ShortTermMemory
from ..tools.base_tool import Tool
from ..tools.tool_registry import ToolRegistry


class ReActAgent:
    """ReAct Agent - 推理与行动交替进行"""
    
    def __init__(
        self,
        llm: LLMClient,
        tools: List[Tool],
        memory: ShortTermMemory,
        max_iterations: int = 15,
        verbose: bool = True
    ):
        """
        初始化ReAct Agent
        
        Args:
            llm: LLM客户端
            tools: 工具列表
            memory: 记忆系统
            max_iterations: 最大迭代次数
            verbose: 是否输出详细过程
        """
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.memory = memory
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # 构建工具描述
        self.tools_description = self._build_tools_description()
        
        logger.info(f"ReAct Agent初始化完成，工具数: {len(tools)}")
    
    def run(self, task: str) -> str:
        """
        执行任务
        
        Args:
            task: 用户任务描述
            
        Returns:
            执行结果
        """
        logger.info(f"开始执行任务: {task}")
        
        # 添加用户任务到记忆
        self.memory.add_message("user", task)
        
        # ReAct循环
        for iteration in range(self.max_iterations):
            if self.verbose:
                logger.info(f"=== 迭代 {iteration + 1} ===")
            
            # 1. 思考：决定下一步行动
            thought = self._think()
            
            if self.verbose:
                logger.info(f"思考: {thought}")
            
            # 2. 检查是否完成
            if self._is_final_answer(thought):
                final_answer = self._extract_final_answer(thought)
                logger.info(f"任务完成: {final_answer}")
                return final_answer
            
            # 3. 解析行动
            action, action_input = self._parse_action(thought)
            
            if not action:
                # 无法解析行动，继续思考
                self.memory.add_message("assistant", thought)
                continue
            
            if self.verbose:
                logger.info(f"行动: {action}, 参数: {action_input}")
            
            # 4. 执行行动
            observation = self._act(action, action_input)
            
            if self.verbose:
                logger.info(f"观察: {observation}")
            
            # 5. 记录到记忆
            self.memory.add_message("assistant", f"{thought}\nObservation: {observation}")
        
        # 达到最大迭代次数
        logger.warning(f"达到最大迭代次数 {self.max_iterations}")
        return "任务执行超时，未能完成。请尝试简化任务或提供更明确的指令。"
    
    def _think(self) -> str:
        """
        思考下一步行动
        
        Returns:
            思考结果（包含Thought和Action）
        """
        # 构建Prompt
        prompt = self._build_prompt()
        
        # 调用LLM
        response = self.llm.generate(prompt)
        
        return response
    
    def _build_prompt(self) -> str:
        """构建Prompt"""
        # 获取对话历史
        history = self.memory.get_history()
        
        # 构建完整Prompt
        prompt = f"""你是一个智能助手，可以使用工具来完成任务。

可用工具：
{self.tools_description}

使用格式：
Thought: 思考下一步应该做什么
Action: 工具名称
Action Input: 工具参数（JSON格式）
Observation: 工具执行结果
... (重复Thought/Action/Observation)
Thought: 我现在知道最终答案了
Final Answer: 最终答案

重要规则：
1. 每次只能使用一个工具
2. Action必须是上述工具之一
3. Action Input必须是有效的JSON格式
4. 完成任务后必须输出Final Answer

对话历史：
{self._format_history(history)}

现在请继续思考并行动："""
        
        return prompt
    
    def _format_history(self, history: List[Dict]) -> str:
        """格式化历史记录"""
        formatted = []
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                formatted.append(f"User: {content}")
            else:
                formatted.append(f"Assistant: {content}")
        return "\n".join(formatted)
    
    def _build_tools_description(self) -> str:
        """构建工具描述"""
        descriptions = []
        for name, tool in self.tools.items():
            desc = f"- {name}: {tool.description}"
            if tool.parameters:
                params = tool.parameters.get("properties", {})
                required = tool.parameters.get("required", [])
                param_desc = ", ".join([
                    f"{k}{'(必需)' if k in required else ''}" 
                    for k in params.keys()
                ])
                desc += f" (参数: {param_desc})"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    def _parse_action(self, thought: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        解析行动
        
        Args:
            thought: 思考结果
            
        Returns:
            (工具名称, 参数字典)
        """
        # 提取Action
        action_match = re.search(r'Action:\s*(\w+)', thought)
        if not action_match:
            return None, None
        
        action = action_match.group(1)
        
        # 提取Action Input
        input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', thought, re.DOTALL)
        if not input_match:
            return action, {}
        
        try:
            import json
            action_input = json.loads(input_match.group(1).strip())
        except:
            # 如果不是JSON，作为字符串处理
            action_input = {"input": input_match.group(1).strip()}
        
        return action, action_input
    
    def _act(self, action: str, action_input: Dict) -> str:
        """
        执行行动
        
        Args:
            action: 工具名称
            action_input: 工具参数
            
        Returns:
            执行结果
        """
        # 检查工具是否存在
        if action not in self.tools:
            return f"错误：未知工具 '{action}'。可用工具: {list(self.tools.keys())}"
        
        tool = self.tools[action]
        
        try:
            # 执行工具
            result = tool.run(**action_input)
            return str(result)
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return f"错误：工具执行失败 - {str(e)}"
    
    def _is_final_answer(self, thought: str) -> bool:
        """检查是否包含最终答案"""
        return "Final Answer:" in thought
    
    def _extract_final_answer(self, thought: str) -> str:
        """提取最终答案"""
        match = re.search(r'Final Answer:\s*(.+)', thought, re.DOTALL)
        if match:
            return match.group(1).strip()
        return thought
    
    def stream_run(self, task: str):
        """
        流式执行任务
        
        Args:
            task: 用户任务描述
            
        Yields:
            执行过程信息
        """
        logger.info(f"开始流式执行任务: {task}")
        
        self.memory.add_message("user", task)
        
        for iteration in range(self.max_iterations):
            yield f"\n=== 步骤 {iteration + 1} ===\n"
            
            # 思考
            thought = self._think()
            yield f"💭 思考: {thought}\n"
            
            # 检查完成
            if self._is_final_answer(thought):
                final_answer = self._extract_final_answer(thought)
                yield f"\n✅ 任务完成!\n{final_answer}\n"
                return
            
            # 解析并执行行动
            action, action_input = self._parse_action(thought)
            
            if action:
                yield f"🔧 行动: {action}\n"
                yield f"📝 参数: {action_input}\n"
                
                observation = self._act(action, action_input)
                yield f"👀 观察: {observation}\n"
                
                self.memory.add_message("assistant", f"{thought}\nObservation: {observation}")
        
        yield "\n⚠️ 达到最大迭代次数\n"
