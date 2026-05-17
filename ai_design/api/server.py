"""AgentOS HITL: User Input Required

AgentOS equivalent of cookbook/03_teams/20_human_in_the_loop/user_input_required.py

A team member's tool requires additional user input before it can execute.
The run pauses and the API response includes the input schema. The client
collects the values and sends them back via continue_run.

Run:
    .venvs/demo/bin/python cookbook/05_agent_os/hitl/user_input_required.py
"""
from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIResponses
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.team import Team
from agno.tools import tool
from agno.skills import LocalSkills, Skills

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

db = SqliteDb(
    db_file="tmp/agent_os_packaging_design.db",
    session_table="packaging_design_sessions",
)

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool(requires_user_input=True, user_input_fields=["destination", "budget"])
def plan_trip(destination: str = "", budget: str = "") -> str:
    """Plan a trip based on user preferences."""
    return (
        f"Trip planned to {destination} with a budget of {budget}. "
        "Includes flights, hotel, and activities."
    )


# ---------------------------------------------------------------------------
# Create members
# ---------------------------------------------------------------------------
# Get the skills directory relative to this file
skills_dir = Path(__file__).parent.parent / "skills"

packaging_design_agent = Agent(
    name="PackagingDesign",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"packaging-design"))]),
    instructions=(
        "外包装设计智能 Agent，根据外包装设计申请单，自动完成从箱体设计、材料设计、方案分析到最终报告生成的全流程设计。"
        "你是外包装设计多智能体系统的**总协调者**。你的职责是：解析设计申请、把控流程进度、按序调度专业子智能体、传递设计上下文，并将最终方案交付用户。"
        "**你不做领域工作**——箱体匹配、材料计算、堆叠分析等专业任务完全由子智能体承担。你的价值在于让整个协作流程顺畅、透明、可追溯。"
    ),
    db=db,
    telemetry=False,
)

box_design_agent = Agent(
    name="BoxDesign",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"box-design"))]),
    instructions=(
        "箱体设计子智能体，在外包装设计流程 Step 1 中被协调智能体调用。接收外包装设计申请单，通过计算最优产品排列方案、确定缓冲余量、从静态箱体配置表中检索匹配箱型，输出推荐箱型及备选方案。"
        "你是外包装设计系统的**箱体设计专家**，负责 Step 1：根据产品参数与运输需求，从标准箱体目录中检索并推荐最优箱型。"
    ),
    db=db,
    telemetry=False,
)


material_design_agent = Agent(
    name="MaterialDesign",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"box-design"))]),
    instructions=(
        "外包装材料设计专业智能体，在外包装多智能体流水线中承接箱体设计结果，输出材料 BOM。"
    ),
    db=db,
    telemetry=False,
)


solution_analysis_agent = Agent(
    name="SolutionAnalysis",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"solution-analysis"))]),
    instructions=(
        "外包装方案分析专业智能体，在外包装多智能体流水线中承接方案分析，输出方案分析结果。"
        "你是外包装设计方案分析多智能体的**总协调者**。你的职责是：把控方案分析流程进度、按序调度专业子智能体、传递设计上下文，并将最终方案分析结果交付用户。"
        "**你不做领域工作**——堆叠分析、成本分析、相似性分析等专业任务完全由子智能体承担。你的价值在于让方案分析三个子子智能体（堆叠分析/成本分析/相似性分析）整个协作流程顺畅、透明、可追溯。"
    ),
    db=db,
    telemetry=False,
)

cost_analysis_agent = Agent(
    name="CostAnalysis",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"cost-analysis"))]),
    instructions=(
        "外包装方案分析专业智能体，在外包装多智能体流水线中承接方案分析，输出方案分析结果。"
        "你是外包装设计方案分析多智能体的**总协调者**。你的职责是：把控方案分析流程进度、按序调度专业子智能体、传递设计上下文，并将最终方案分析结果交付用户。"
        "**你不做领域工作**——堆叠分析、成本分析、相似性分析等专业任务完全由子智能体承担。你的价值在于让方案分析三个子子智能体（堆叠分析/成本分析/相似性分析）整个协作流程顺畅、透明、可追溯。"
    ),
    db=db,
    telemetry=False,
)

similarity_analysis_agent = Agent(
    name="SimilarityAnalysis",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"similarity-analysis"))]),
    instructions=(
        "外包装方案相似性分析专业智能体，在外包装方案分析多智能体流水线中承接相似性分析，输出相似方案"
    ),
    db=db,
    telemetry=False,
)

stacking_analysis_agent = Agent(
    name="StackingAnalysis",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"stacking-analysis"))]),
    instructions=(
        "外包装方案相似性分析专业智能体，在外包装方案分析多智能体流水线中承接相似性分析，输出相似方案"
    ),
    db=db,
    telemetry=False,
)

solution_consolidation_agent = Agent(
    name="SolutionConsolidation",
    model=OpenAIResponses(id="gpt-5-mini"),
    tools=[],
    skills=Skills(loaders=[LocalSkills(str(skills_dir/"solution-consolidation"))]),
    instructions=(
        "外包装方案整理专业智能体，在外包装方案分析多智能体流水线中承接所有步骤的结果，整理并输出最终外包装方案"
    ),
    db=db,
    telemetry=False,
)
# ---------------------------------------------------------------------------
# Create team
# ---------------------------------------------------------------------------

packaging_design_team = Team(
    id="packaging-design-team",
    name="PackagingDesignTeam",
    model=OpenAIResponses(id="gpt-5-mini"),
    members=[packaging_design_agent, box_design_agent, material_design_agent, solution_analysis_agent, cost_analysis_agent, similarity_analysis_agent, stacking_analysis_agent, solution_consolidation_agent],
    instructions="外包装设计智能 Agent，根据外包装设计申请单，自动完成从箱体设计、材料设计、方案分析到最终报告生成的全流程设计。",
    db=db,
    telemetry=False,
    add_history_to_context=True,
)

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
# Setup our AgentOS app
agent_os = AgentOS(
    teams=[packaging_design_team],
    interfaces=[AGUI(team=packaging_design_team)],
)
app = agent_os.get_app()

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Run your AgentOS.

    You can see the configuration and available apps at:
    http://localhost:9001/config

    Use Port 9001 for Dojo compatibility.
    """
    agent_os.serve(app="server:app", host="127.0.0.1", port=9001)
