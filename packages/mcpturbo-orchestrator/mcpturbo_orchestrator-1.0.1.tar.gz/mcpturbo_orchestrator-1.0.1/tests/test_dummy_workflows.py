import pytest
from mcpturbo_orchestrator import ProjectOrchestrator, Workflow, Task, WorkflowStatus
from mcpturbo_agents.base_agent import LocalAgent

class DummyAgent(LocalAgent):
    def __init__(self, agent_id="dummy"):
        super().__init__(agent_id, "Dummy Agent")

    async def handle_request(self, request):
        return request.data

class FailingAgent(LocalAgent):
    def __init__(self):
        super().__init__("fail", "Failing Agent")

    async def handle_request(self, request):
        raise Exception("boom")

@pytest.mark.asyncio
async def test_workflow_success_path():
    orch = ProjectOrchestrator()
    agent = DummyAgent()
    orch.register_agent(agent)
    tasks = [
        Task(id="t1", agent_id=agent.config.agent_id, action="echo", data={"a": 1}),
        Task(id="t2", agent_id=agent.config.agent_id, action="echo", data={}, dependencies=["t1"]),
    ]
    wf = Workflow(id="wf_success", name="Success", tasks=tasks)
    orch.workflows[wf.id] = wf

    result = await orch.execute_workflow(wf.id)
    assert result["status"] == WorkflowStatus.COMPLETED.value
    results = {t["id"]: t["result"] for t in result["tasks"]}
    assert results["t1"] == {"a": 1}
    assert results["t2"] == {"t1_result": {"a": 1}}

@pytest.mark.asyncio
async def test_workflow_failure_path():
    orch = ProjectOrchestrator()
    agent = FailingAgent()
    orch.register_agent(agent)
    tasks = [
        Task(id="t1", agent_id=agent.config.agent_id, action="fail", data={}, retry_attempts=1),
        Task(id="t2", agent_id=agent.config.agent_id, action="fail", data={}, dependencies=["t1"]),
    ]
    wf = Workflow(id="wf_fail", name="Fail", tasks=tasks)
    orch.workflows[wf.id] = wf

    result = await orch.execute_workflow(wf.id)
    assert result["status"] == WorkflowStatus.FAILED.value
    statuses = {t["id"]: t["status"] for t in result["tasks"]}
    assert statuses["t1"] == WorkflowStatus.FAILED.value
    assert statuses["t2"] == WorkflowStatus.PENDING.value
