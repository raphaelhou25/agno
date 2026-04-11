from pydantic import BaseModel

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.workflow import Workflow, StepOutput, StepInput, Step, pause
from agno.workflow.types import UserInputField

#
# @pause(
#     name="pause_step_design_box",
#     requires_user_input=True,
#     user_input_message="Box Size Info",
#     user_input_schema=[
#         UserInputField(name="length", field_type="str", description="Length of box", required=True)
#     ]
# )
def step_design_box_for_box_size(step_input: StepInput)->StepOutput:
    print("Design Box...")
    return StepOutput(
        content="Box design complete:\n"
        "- 1000 records gathered\n"
        "- Ready for optional advanced processing"
    )

class ProcessMainEntity(BaseModel):
    name: str

# step_design_box = Step(
#     name="Design Box Step",
#     executor=step_design_box
# )


step_design_box = Step(
    name="Design Box Step",
    requires_user_input=True,
    user_input_message="Box Size Info",
    user_input_schema=[
        UserInputField(name="length", field_type="str", description="Length of box", required=True) #type: ignore
    ],
    executor=step_design_box_for_box_size
)

workflow_packaging_design = Workflow(
    id="packaging_design_workflow",
    name="packaging_design_workflow",
    description="Packaging design workflow.",
    # db=SqliteDb(
    #     session_table="workflow_session",
    #     db_file="tmp/workflow.db",
    # ),
    steps=[step_design_box],
    input_schema=ProcessMainEntity
)

agent_os_design = AgentOS(
    id="agentos-design",
    # name="agentos-design",
    description="design agent",
    workflows=[workflow_packaging_design]
)

app = agent_os_design.get_app()

if __name__=="__main__":
    agent_os_design.serve(app="workflow_agent:app", host="0.0.0.0", port=7788, reload=True)
