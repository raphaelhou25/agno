"""
Agno Assist
==========

Demonstrates a minimal agno agent.
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.mcp import MCPTools

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------

agno_assist = Agent(
    name="Agno Assist",
    # model=Claude(id="claude-sonnet-4-5"),
    model=OpenAIChat(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
    ),
    db=SqliteDb(db_file="agno.db"),
    tools=[MCPTools(url="https://docs.agno.com/mcp")],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
)

agent_os = AgentOS(agents=[agno_assist])
app = agent_os.get_app()

# ---------------------------------------------------------------------------
# Run Agent
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent_os.serve(app="agno_assist:app", reload=True)
