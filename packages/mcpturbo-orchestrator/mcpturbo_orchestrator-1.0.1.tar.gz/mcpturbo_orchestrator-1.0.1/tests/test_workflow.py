import asyncio
import pytest

from mcpturbo_core.protocol import protocol
from mcpturbo_orchestrator import ProjectOrchestrator, Task, Workflow, TaskPriority, WorkflowStatus
from mcpturbo_agents.base_agent import LocalAgent


class EchoAgent(LocalAgent):
    def __init__(self):
        super().__init__("echo", "Echo Agent")

    async def handle_request(self, request):
        return request.data


@pytest.mark.asyncio
async def test_simple_workflow_execution():
    protocol.agents.clear()
    orchestrator = ProjectOrchestrator()
    agent = EchoAgent()
    orchestrator.register_agent(agent)

    tasks = [
        Task(id="t1", agent_id="echo", action="echo", data={"msg": "hi"}),
        Task(id="t2", agent_id="echo", action="echo", data={}, dependencies=["t1"]),
    ]
    wf = Workflow(id="wf1", name="Echo", tasks=tasks)
    orchestrator.workflows[wf.id] = wf

    result = await orchestrator.execute_workflow(wf.id)
    assert result["status"] == WorkflowStatus.COMPLETED.value
    task_results = {t["id"]: t["result"] for t in result["tasks"]}
    assert task_results["t1"] == {"msg": "hi"}
    assert task_results["t2"] == {"t1_result": {"msg": "hi"}}
