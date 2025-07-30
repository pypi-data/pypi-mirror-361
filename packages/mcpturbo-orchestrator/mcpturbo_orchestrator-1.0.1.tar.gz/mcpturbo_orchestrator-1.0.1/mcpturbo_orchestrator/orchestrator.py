import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from mcpturbo_core.protocol import protocol
from mcpturbo_core.messages import Request, Response, Event, create_request
from mcpturbo_core.exceptions import MCPError, TimeoutError
from mcpturbo_agents import BaseAgent

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    id: str
    agent_id: str
    action: str
    data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 60
    retry_attempts: int = 3
    
    # Runtime fields
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0

@dataclass
class Workflow:
    id: str
    name: str
    tasks: List[Task]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies completed)"""
        ready_tasks = []
        
        for task in self.tasks:
            if task.status != WorkflowStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            deps_completed = all(
                any(t.id == dep_id and t.status == WorkflowStatus.COMPLETED 
                    for t in self.tasks)
                for dep_id in task.dependencies
            )
            
            if not task.dependencies or deps_completed:
                ready_tasks.append(task)
        
        # Sort by priority
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        return ready_tasks
    
    def is_completed(self) -> bool:
        """Check if workflow is completed"""
        return all(task.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] 
                  for task in self.tasks)
    
    def has_failed(self) -> bool:
        """Check if workflow has failed tasks"""
        return any(task.status == WorkflowStatus.FAILED for task in self.tasks)

class ProjectOrchestrator:
    """Advanced orchestrator for coordinating multiple AI agents"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}
        self.max_concurrent_workflows = 5
        self.max_concurrent_tasks = 10
        
        # Workflow templates for common patterns
        self.workflow_templates: Dict[str, Callable] = {
            "app_generation": self._create_app_generation_workflow,
            "code_review": self._create_code_review_workflow,
            "architecture_design": self._create_architecture_workflow
        }
    
    def register_agent(self, agent: BaseAgent, **config):
        """Register an agent with the orchestrator"""
        self.agents[agent.config.agent_id] = agent
        protocol.register_agent(agent.config.agent_id, agent, **config)
    
    def register_workflow_template(self, name: str, template_func: Callable):
        """Register a custom workflow template"""
        self.workflow_templates[name] = template_func
    
    def subscribe_to_events(self, event: str, handler: Callable):
        """Subscribe to workflow events"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def create_workflow_from_template(self, template_name: str, **kwargs) -> str:
        """Create workflow from predefined template"""
        if template_name not in self.workflow_templates:
            raise MCPError(f"Workflow template '{template_name}' not found")
        
        workflow = self.workflow_templates[template_name](**kwargs)
        self.workflows[workflow.id] = workflow
        
        await self._emit_event("workflow_created", {
            "workflow_id": workflow.id,
            "template": template_name,
            "tasks_count": len(workflow.tasks)
        })
        
        return workflow.id
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow asynchronously"""
        if workflow_id not in self.workflows:
            raise MCPError(f"Workflow '{workflow_id}' not found")
        
        workflow = self.workflows[workflow_id]
        if workflow.status != WorkflowStatus.PENDING:
            raise MCPError(f"Workflow '{workflow_id}' is not in pending state")
        
        # Start workflow execution
        task = asyncio.create_task(self._execute_workflow_internal(workflow))
        self.running_workflows[workflow_id] = task
        
        try:
            result = await task
            return result
        finally:
            self.running_workflows.pop(workflow_id, None)
    
    async def _execute_workflow_internal(self, workflow: Workflow) -> Dict[str, Any]:
        """Internal workflow execution logic"""
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        await self._emit_event("workflow_started", {
            "workflow_id": workflow.id,
            "name": workflow.name
        })
        
        try:
            # Execute tasks with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
            completed_tasks = 0
            
            while completed_tasks < len(workflow.tasks) and not workflow.has_failed():
                ready_tasks = workflow.get_ready_tasks()
                
                if not ready_tasks:
                    # Wait a bit for dependencies to complete
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks concurrently
                task_coroutines = [
                    self._execute_task_with_semaphore(semaphore, workflow, task)
                    for task in ready_tasks
                ]
                
                if task_coroutines:
                    await asyncio.gather(*task_coroutines, return_exceptions=True)
                
                # Count completed tasks
                completed_tasks = sum(1 for task in workflow.tasks 
                                    if task.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED])
            
            # Determine final workflow status
            if workflow.has_failed():
                workflow.status = WorkflowStatus.FAILED
            else:
                workflow.status = WorkflowStatus.COMPLETED
            
            workflow.completed_at = datetime.utcnow()
            
            await self._emit_event("workflow_completed", {
                "workflow_id": workflow.id,
                "status": workflow.status.value,
                "duration": (workflow.completed_at - workflow.started_at).total_seconds()
            })
            
            return self._generate_workflow_result(workflow)
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            
            await self._emit_event("workflow_failed", {
                "workflow_id": workflow.id,
                "error": str(e)
            })
            
            raise MCPError(f"Workflow execution failed: {str(e)}")
    
    async def _execute_task_with_semaphore(self, semaphore: asyncio.Semaphore, 
                                          workflow: Workflow, task: Task):
        """Execute a single task with concurrency control"""
        async with semaphore:
            await self._execute_task(workflow, task)
    
    async def _execute_task(self, workflow: Workflow, task: Task):
        """Execute a single task"""
        if task.status != WorkflowStatus.PENDING:
            return
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.utcnow()
        task.attempts += 1
        
        await self._emit_event("task_started", {
            "workflow_id": workflow.id,
            "task_id": task.id,
            "agent_id": task.agent_id,
            "action": task.action
        })
        
        try:
            # Prepare task data with workflow context
            task_data = {**task.data}
            task_data.update(workflow.context)
            
            # Add results from completed dependencies
            for dep_id in task.dependencies:
                dep_task = next((t for t in workflow.tasks if t.id == dep_id), None)
                if dep_task and dep_task.status == WorkflowStatus.COMPLETED:
                    task_data[f"{dep_id}_result"] = dep_task.result
            
            # Send request to agent
            response = await protocol.send_request(
                sender_id="orchestrator",
                target_id=task.agent_id,
                action=task.action,
                data=task_data,
                timeout=task.timeout
            )
            
            task.result = response.result if response.success else None
            task.error = response.error if not response.success else None
            task.status = WorkflowStatus.COMPLETED if response.success else WorkflowStatus.FAILED
            
        except Exception as e:
            task.error = str(e)
            task.status = WorkflowStatus.FAILED
            
            # Retry logic
            if task.attempts < task.retry_attempts:
                task.status = WorkflowStatus.PENDING
                await asyncio.sleep(2 ** task.attempts)  # Exponential backoff
        
        task.completed_at = datetime.utcnow()
        
        await self._emit_event("task_completed", {
            "workflow_id": workflow.id,
            "task_id": task.id,
            "status": task.status.value,
            "attempts": task.attempts
        })
    
    def _generate_workflow_result(self, workflow: Workflow) -> Dict[str, Any]:
        """Generate final workflow result"""
        return {
            "workflow_id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "tasks": [
                {
                    "id": task.id,
                    "agent_id": task.agent_id,
                    "action": task.action,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                    "duration": (task.completed_at - task.started_at).total_seconds() 
                               if task.started_at and task.completed_at else None
                }
                for task in workflow.tasks
            ],
            "duration": (workflow.completed_at - workflow.started_at).total_seconds()
                       if workflow.started_at and workflow.completed_at else None,
            "context": workflow.context
        }
    
    async def _emit_event(self, event: str, data: Dict[str, Any]):
        """Emit workflow event"""
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception:
                continue
    
    # Workflow Templates
    
    def _create_app_generation_workflow(self, **kwargs) -> Workflow:
        """Create workflow for complete app generation"""
        import uuid
        
        workflow_id = str(uuid.uuid4())
        app_name = kwargs.get("app_name", "MyApp")
        
        tasks = [
            Task(
                id="architecture",
                agent_id="claude",  # Claude is good at architecture
                action="reasoning", 
                data={
                    "prompt": f"Design the architecture for a {kwargs.get('app_type', 'web')} application called {app_name}. Include: database schema, API endpoints, frontend components, and deployment strategy.",
                    "system_prompt": "You are a senior software architect. Provide detailed technical specifications."
                },
                priority=TaskPriority.CRITICAL
            ),
            Task(
                id="backend_code",
                agent_id="openai",  # OpenAI for general code generation
                action="code_generation",
                data={
                    "prompt": f"Generate backend code for {app_name} application",
                    "language": "python"
                },
                dependencies=["architecture"],
                priority=TaskPriority.HIGH
            ),
            Task(
                id="frontend_code", 
                agent_id="deepseek",  # DeepSeek for fast frontend code
                action="fast_coding",
                data={
                    "prompt": f"Generate React frontend for {app_name}",
                    "language": "typescript"
                },
                dependencies=["architecture"],
                priority=TaskPriority.HIGH
            ),
            Task(
                id="optimization",
                agent_id="deepseek",
                action="code_optimization", 
                data={
                    "optimization_type": "performance"
                },
                dependencies=["backend_code", "frontend_code"],
                priority=TaskPriority.NORMAL
            )
        ]
        
        return Workflow(
            id=workflow_id,
            name=f"Generate {app_name} Application",
            tasks=tasks,
            context={"app_name": app_name, **kwargs}
        )
    
    def _create_code_review_workflow(self, **kwargs) -> Workflow:
        """Create workflow for code review process"""
        import uuid
        
        workflow_id = str(uuid.uuid4())
        code = kwargs.get("code", "")
        
        tasks = [
            Task(
                id="analysis",
                agent_id="claude",
                action="analysis",
                data={
                    "content": code,
                    "analysis_type": "code_review"
                },
                priority=TaskPriority.HIGH
            ),
            Task(
                id="optimization_suggestions",
                agent_id="deepseek", 
                action="code_optimization",
                data={
                    "code": code,
                    "optimization_type": "readability"
                },
                dependencies=["analysis"],
                priority=TaskPriority.NORMAL
            ),
            Task(
                id="security_check",
                agent_id="openai",
                action="generate_text",
                data={
                    "prompt": f"Analyze this code for security vulnerabilities:\n\n{code}",
                    "system_prompt": "You are a cybersecurity expert. Focus on identifying potential security issues."
                },
                dependencies=["analysis"],
                priority=TaskPriority.HIGH
            )
        ]
        
        return Workflow(
            id=workflow_id,
            name="Code Review Process",
            tasks=tasks,
            context={"original_code": code}
        )
    
    def _create_architecture_workflow(self, **kwargs) -> Workflow:
        """Create workflow for architecture design"""
        import uuid
        
        workflow_id = str(uuid.uuid4())
        requirements = kwargs.get("requirements", "")
        
        tasks = [
            Task(
                id="requirements_analysis",
                agent_id="claude",
                action="reasoning",
                data={
                    "prompt": f"Analyze these requirements and suggest technical architecture: {requirements}"
                },
                priority=TaskPriority.CRITICAL
            ),
            Task(
                id="database_design",
                agent_id="openai",
                action="generate_text",
                data={
                    "prompt": "Design database schema based on the architecture analysis",
                    "system_prompt": "You are a database architect. Design efficient, normalized schemas."
                },
                dependencies=["requirements_analysis"],
                priority=TaskPriority.HIGH
            ),
            Task(
                id="api_design",
                agent_id="deepseek",
                action="fast_coding",
                data={
                    "prompt": "Generate OpenAPI specification for the designed system",
                    "language": "yaml"
                },
                dependencies=["requirements_analysis", "database_design"],
                priority=TaskPriority.NORMAL
            )
        ]
        
        return Workflow(
            id=workflow_id,
            name="Architecture Design",
            tasks=tasks,
            context={"requirements": requirements}
        )
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        if workflow_id not in self.workflows:
            raise MCPError(f"Workflow '{workflow_id}' not found")
        
        workflow = self.workflows[workflow_id]
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": sum(1 for task in workflow.tasks 
                           if task.status == WorkflowStatus.COMPLETED) / len(workflow.tasks) * 100,
            "tasks_status": {
                task.id: {
                    "status": task.status.value,
                    "agent": task.agent_id,
                    "attempts": task.attempts
                }
                for task in workflow.tasks
            }
        }
    
    async def cancel_workflow(self, workflow_id: str):
        """Cancel a running workflow"""
        if workflow_id in self.running_workflows:
            task = self.running_workflows[workflow_id]
            task.cancel()
        
        if workflow_id in self.workflows:
            self.workflows[workflow_id].status = WorkflowStatus.CANCELLED

# Singleton instance
orchestrator = ProjectOrchestrator()