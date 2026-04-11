from pathlib import Path
from typing import Any

from pydantic import BaseModel

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.skills import Skills, LocalSkills
from agno.tools import tool

skills_dir = Path(__file__).parent / "skills"


class ProcessMainEntity(BaseModel):
    task: str
    task_detail: str


@tool(requires_user_input=True, user_input_fields=["length"])
def tool_box_design(length: str):
    """
    箱体设计：该工具用于箱体设计
    Args:
        length: 包装箱长度

    Returns:

    """
    print(f"\033[32mTool-BoxDesign >> \033[0m box design, length: {length}")
    result = {
        "length": length,
        "width": "12",
        "height": "13"
    }
    return f"Box Design Result: {result}"


agent_design = Agent(
    name="DesignAgent",
    model=DeepSeek(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
    ),
    instructions="""
    你是一个专业的包装设计智能体，拥有以下能力：

    **工具集**
    - 箱体设计：用于设计箱体尺寸
    """,
    tools=[tool_box_design],
    skills=Skills(loaders=[LocalSkills(path=str(skills_dir))]),
    input_schema=ProcessMainEntity,
    debug_mode=True,
)

agent_os_design = AgentOS(
    agents=[agent_design],
    interfaces=[AGUI(agent=agent_design)]
)

app = agent_os_design.get_app()

if __name__ == "__main__":
    agent_os_design.serve(
        app="agui_agent_with_skills:app",
        port=7787,
        reload=False,
    )
