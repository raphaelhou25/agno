"""Async router handling exposing an Agno Agent or Team in an AG-UI compatible format."""

import uuid
from typing import AsyncIterator, Optional, Union

from agno.run.requirement import RunRequirement
from agno.utils.log import log_error

try:
    from ag_ui.core import (
        BaseEvent,
        EventType,
        RunAgentInput,
        RunErrorEvent,
        RunStartedEvent,
    )
    from ag_ui.encoder import EventEncoder
except ImportError as e:
    raise ImportError("`ag_ui` not installed. Please install it with `pip install -U ag-ui-protocol`") from e

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from agno.agent import Agent, RemoteAgent
from agno.os.interfaces.agui.utils import (
    async_stream_agno_response_as_agui_events,
    extract_agui_user_input,
    validate_agui_state,
)
from agno.team.remote import RemoteTeam
from agno.team.team import Team


async def run_agent(agent: Union[Agent, RemoteAgent], run_input: RunAgentInput) -> AsyncIterator[BaseEvent]:
    """Run the contextual Agent, mapping AG-UI input messages to Agno format, and streaming the response in AG-UI format."""
    run_id = run_input.run_id or str(uuid.uuid4())

    try:
        # AG-UI frontends send full conversation history every request.
        # Extract only the last user message — agent manages history via session DB.
        user_input = extract_agui_user_input(run_input.messages or [])

        yield RunStartedEvent(type=EventType.RUN_STARTED, thread_id=run_input.thread_id, run_id=run_id)

        # Look for user_id in run_input.forwarded_props
        user_id = None
        if run_input.forwarded_props and isinstance(run_input.forwarded_props, dict):
            user_id = run_input.forwarded_props.get("user_id")

        # Validating the session state is of the expected type (dict)
        session_state = validate_agui_state(run_input.state, run_input.thread_id)


        # 检测是否为 HITL continue 请求
        requirements_data = None
        if run_input.forwarded_props and isinstance(run_input.forwarded_props, dict):
            requirements_data = run_input.forwarded_props.get("requirements")

        if requirements_data:
            # 反序列化 requirements
            requirements = [
                RunRequirement.from_dict(r) if isinstance(r, dict) else r
                for r in requirements_data
            ]
            # 调用 acontinue_run，run_id 来自 run_input.run_id（前端必须传入暂停时的 run_id）
            response_stream = agent.acontinue_run(  # type: ignore
                # input=user_input, # 考虑HITL执行完成后，用户一并输入了其他内容，是否有这种业务场景
                run_id=run_id,
                session_id=run_input.thread_id,
                requirements=requirements,
                stream=True,
                stream_events=True,
                # session_state=session_state, # 思考：session_state有什么用，在continue 逻辑中是否需要
                user_id=user_id,
            )
        else:
            # Request streaming response from agent
            response_stream = agent.arun(  # type: ignore
                input=user_input,
                session_id=run_input.thread_id,
                stream=True,
                stream_events=True,
                user_id=user_id,
                session_state=session_state,
                run_id=run_id,
            )

        # Stream the response content in AG-UI format
        async for event in async_stream_agno_response_as_agui_events(
            response_stream=response_stream,  # type: ignore
            thread_id=run_input.thread_id,
            run_id=run_id,
        ):
            yield event

    # Emit a RunErrorEvent if any error occurs
    except Exception as e:
        log_error(f"Error running agent: {str(e)}")
        yield RunErrorEvent(type=EventType.RUN_ERROR, message=str(e))


async def run_team(team: Union[Team, RemoteTeam], input: RunAgentInput) -> AsyncIterator[BaseEvent]:
    """Run the contextual Team, mapping AG-UI input messages to Agno format, and streaming the response in AG-UI format."""
    run_id = input.run_id or str(uuid.uuid4())
    try:
        # AG-UI frontends send full conversation history every request.
        # Extract only the last user message — team manages history via session DB.
        user_input = extract_agui_user_input(input.messages or [])
        yield RunStartedEvent(type=EventType.RUN_STARTED, thread_id=input.thread_id, run_id=run_id)

        # Look for user_id in input.forwarded_props
        user_id = None
        if input.forwarded_props and isinstance(input.forwarded_props, dict):
            user_id = input.forwarded_props.get("user_id")

        # Validating the session state is of the expected type (dict)
        session_state = validate_agui_state(input.state, input.thread_id)

        # Request streaming response from team
        response_stream = team.arun(  # type: ignore
            input=user_input,
            session_id=input.thread_id,
            stream=True,
            stream_steps=True,
            user_id=user_id,
            session_state=session_state,
            run_id=run_id,
        )

        # Stream the response content in AG-UI format
        async for event in async_stream_agno_response_as_agui_events(
            response_stream=response_stream, thread_id=input.thread_id, run_id=run_id
        ):
            yield event

    except Exception as e:
        log_error(f"Error running team: {str(e)}")
        yield RunErrorEvent(type=EventType.RUN_ERROR, message=str(e))


def attach_routes(
    router: APIRouter, agent: Optional[Union[Agent, RemoteAgent]] = None, team: Optional[Union[Team, RemoteTeam]] = None
) -> APIRouter:
    if agent is None and team is None:
        raise ValueError("Either agent or team must be provided.")

    encoder = EventEncoder()

    @router.post(
        "/agui",
        name="run_agent",
    )
    async def run_agent_agui(run_input: RunAgentInput):
        async def event_generator():
            if agent:
                async for event in run_agent(agent, run_input):
                    encoded_event = encoder.encode(event)
                    yield encoded_event
            elif team:
                async for event in run_team(team, run_input):
                    encoded_event = encoder.encode(event)
                    yield encoded_event

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
        )

    @router.get("/status")
    async def get_status():
        return {"status": "available"}

    return router
