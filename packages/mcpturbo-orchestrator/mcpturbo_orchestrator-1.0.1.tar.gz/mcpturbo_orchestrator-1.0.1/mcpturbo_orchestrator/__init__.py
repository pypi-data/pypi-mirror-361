"""
MCPturbo Orchestrator - Intelligent Agent Orchestration & Coordination v2

Advanced workflow management and agent coordination system.
"""

__version__ = "2.0.0"
__author__ = "Federico Monfasani"

# Core orchestration classes
from .orchestrator import (
    ProjectOrchestrator, Workflow, Task, 
    WorkflowStatus, TaskPriority, orchestrator
)

# Main exports
__all__ = [
    # Core classes
    "ProjectOrchestrator",
    "Workflow", 
    "Task",
    
    # Enums
    "WorkflowStatus",
    "TaskPriority",
    
    # Global instance
    "orchestrator",
    
    # Metadata
    "__version__",
    "__author__"
]

# Convenience functions
async def quick_workflow(template_name: str, **kwargs) -> str:
    """Create and execute workflow from template"""
    workflow_id = await orchestrator.create_workflow_from_template(template_name, **kwargs)
    result = await orchestrator.execute_workflow(workflow_id)
    return result

async def generate_app(app_name: str, app_type: str = "web", **kwargs) -> dict:
    """Quick app generation workflow"""
    return await quick_workflow("app_generation", app_name=app_name, app_type=app_type, **kwargs)

async def review_code(code: str, **kwargs) -> dict:
    """Quick code review workflow"""
    return await quick_workflow("code_review", code=code, **kwargs)

async def design_architecture(requirements: str, **kwargs) -> dict:
    """Quick architecture design workflow"""
    return await quick_workflow("architecture_design", requirements=requirements, **kwargs)

# Workflow templates available
AVAILABLE_TEMPLATES = [
    "app_generation",
    "code_review", 
    "architecture_design"
]

# Setup function for orchestrator
async def setup_orchestrator(*agents, **config):
    """Setup orchestrator with agents"""
    for agent in agents:
        orchestrator.register_agent(agent, **config)
    
    return orchestrator