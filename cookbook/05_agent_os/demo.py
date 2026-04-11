"""
AgentOS Demo

Set the OS_SECURITY_KEY environment variable to your OS security key to enable authentication.

Prerequisites:
uv pip install -U fastapi uvicorn sqlalchemy pgvector psycopg openai ddgs yfinance
"""

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.knowledge.knowledge import Knowledge
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.team import Team
from agno.tools.mcp import MCPTools
from agno.tools.websearch import WebSearchTools
from agno.vectordb.pgvector import PgVector

# ---------------------------------------------------------------------------
# Create Example
# ---------------------------------------------------------------------------

# Database connection
db_url = "postgresql+psycopg://ai:ai@127.0.0.1:5432/ai"

# Create Postgres-backed memory store
db = PostgresDb(db_url=db_url)
# db = SqliteDb(
#     db_file="agno.db",
#     session_table="sessions",
#     eval_table="eval_runs",
#     memory_table="user_memories",
#     metrics_table="metrics",
# )

# Create Postgres-backed vector store
vector_db = PgVector(
    db_url=db_url,
    table_name="agno_docs",
)

knowledge = Knowledge(
    name="Agno Docs",
    contents_db=db,
    vector_db=vector_db,
)

# Create your agents
agno_agent = Agent(
    name="Agno Agent",
    # model=OpenAIChat(id="gpt-4.1"),
    model=DeepSeek(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
                     ),
    tools=[MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")],
    db=db,
    update_memory_on_run=True,
    knowledge=knowledge,
    markdown=True,
)

simple_agent = Agent(
    name="Simple Agent",
    role="Simple agent",
    id="simple_agent",
    model=DeepSeek(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
    ),
    instructions=["You are a simple agent"],
    db=db,
    update_memory_on_run=True,
)

research_agent = Agent(
    name="Research Agent",
    role="Research agent",
    id="research_agent",
    model=DeepSeek(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
    ),
    instructions=["You are a research agent"],
    tools=[WebSearchTools()],
    db=db,
    update_memory_on_run=True,
)

# Create a team
research_team = Team(
    name="Research Team",
    description="A team of agents that research the web",
    members=[research_agent, simple_agent],
    model=DeepSeek(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
    ),
    id="research_team",
    instructions=[
        "You are the lead researcher of a research team.",
    ],
    db=db,
    update_memory_on_run=True,
    add_datetime_to_context=True,
    markdown=True,
)

# Create the AgentOS
agent_os = AgentOS(
    id="agentos-demo",
    agents=[agno_agent],
    teams=[research_team],
)
app = agent_os.get_app()


# ---------------------------------------------------------------------------
# Run Example
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent_os.serve(app="demo:app", port=7777, reload=True)
