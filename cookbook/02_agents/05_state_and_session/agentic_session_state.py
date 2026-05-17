"""
Agentic Session State
=============================

Agentic Session State.
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIResponses

db = SqliteDb(db_file="tmp/agents.db")
# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
agent = Agent(
    model=DeepSeek(
        id="deepseek-chat",
        name="deepseek-chat",
        api_key="sk-7b4ab126e7d6479db21b74a4addc9a39",
        base_url="https://api.deepseek.com"
    ),
    db=db,
    session_state={"shopping_list": []},
    add_session_state_to_context=True,  # Required so the agent is aware of the session state
    enable_agentic_state=True,
)

# ---------------------------------------------------------------------------
# Run Agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent.print_response("Add milk, eggs, and bread to the shopping list")

    agent.print_response("I picked up the eggs, now what's on my list?")

    print(f"Session state: {agent.get_session_state()}")
