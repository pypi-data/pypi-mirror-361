import os
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.extend([
    str(ROOT / "packages" / "agents"),
    str(ROOT / "packages" / "core"),
    str(ROOT),
])

from mcpturbo_orchestrator import ProjectOrchestrator, Workflow, Task, WorkflowStatus
from mcpturbo_agents import GenesisAgent, AgentConfig, AgentType


@pytest.mark.asyncio
async def test_simple_workflow_execution():
    orch = ProjectOrchestrator()
    agent = GenesisAgent(AgentConfig(agent_id="gen-wf", name="Genesis WF", agent_type=AgentType.LOCAL))
    orch.register_agent(agent)

    workflow = Workflow(
        id="wf1",
        name="Test Workflow",
        tasks=[Task(id="t1", agent_id="gen-wf", action="echo", data={"msg": "hi"})],
    )
    orch.workflows["wf1"] = workflow

    result = await orch.execute_workflow("wf1")
    assert result["status"] == WorkflowStatus.COMPLETED.value
