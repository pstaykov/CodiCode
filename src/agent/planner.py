"""
Task planning module for breaking down user requests into steps.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class StepStatus(Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """
    Represents a single step in the execution plan.
    """
    id: int
    description: str
    tool: Optional[str] = None
    parameters: Optional[Dict] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "tool": self.tool,
            "parameters": self.parameters,
            "status": self.status.value,
            "result": self.result,
            "error": self.error
        }


class TaskPlanner:
    """
    Plans and manages task execution steps.
    Breaks down high-level requests into actionable steps.
    """

    def __init__(self):
        self.current_plan: List[PlanStep] = []
        self.step_counter = 0

    def create_plan_from_llm_response(self, llm_reasoning: str) -> List[PlanStep]:
        """
        Create a plan based on LLM's reasoning.
        In a real implementation, this would parse structured output.

        For now, we create a simple default plan structure.
        """
        # This is a placeholder - in production, the LLM would output
        # structured steps that we parse here
        steps = []

        # Simple heuristic-based planning
        if "read" in llm_reasoning.lower() or "find" in llm_reasoning.lower():
            steps.append(PlanStep(
                id=self._next_id(),
                description="Search and read relevant files",
                tool="search_files",
                status=StepStatus.PENDING
            ))

        if "write" in llm_reasoning.lower() or "create" in llm_reasoning.lower():
            steps.append(PlanStep(
                id=self._next_id(),
                description="Write or modify files",
                tool="write_file",
                status=StepStatus.PENDING
            ))

        if "test" in llm_reasoning.lower() or "run" in llm_reasoning.lower():
            steps.append(PlanStep(
                id=self._next_id(),
                description="Execute tests or commands",
                tool="run_shell",
                status=StepStatus.PENDING
            ))

        # Default fallback
        if not steps:
            steps.append(PlanStep(
                id=self._next_id(),
                description="Execute task",
                status=StepStatus.PENDING
            ))

        self.current_plan = steps
        return steps

    def add_step(self, description: str, tool: str = None, parameters: Dict = None) -> PlanStep:
        """Add a new step to the current plan."""
        step = PlanStep(
            id=self._next_id(),
            description=description,
            tool=tool,
            parameters=parameters,
            status=StepStatus.PENDING
        )
        self.current_plan.append(step)
        return step

    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next pending step to execute."""
        for step in self.current_plan:
            if step.status == StepStatus.PENDING:
                return step
        return None

    def mark_step_in_progress(self, step_id: int) -> None:
        """Mark a step as in progress."""
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.IN_PROGRESS

    def mark_step_completed(self, step_id: int, result: str = None) -> None:
        """Mark a step as completed."""
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.COMPLETED
            step.result = result

    def mark_step_failed(self, step_id: int, error: str) -> None:
        """Mark a step as failed."""
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.FAILED
            step.error = error

    def is_plan_complete(self) -> bool:
        """Check if all steps are completed."""
        if not self.current_plan:
            return True

        return all(
            step.status == StepStatus.COMPLETED
            for step in self.current_plan
        )

    def has_failed_steps(self) -> bool:
        """Check if any steps have failed."""
        return any(
            step.status == StepStatus.FAILED
            for step in self.current_plan
        )

    def get_plan_summary(self) -> str:
        """Get a human-readable summary of the plan."""
        if not self.current_plan:
            return "No plan created yet."

        lines = ["Current Plan:"]
        for step in self.current_plan:
            status_icon = {
                StepStatus.PENDING: "⭘",
                StepStatus.IN_PROGRESS: "⟳",
                StepStatus.COMPLETED: "✓",
                StepStatus.FAILED: "✗"
            }.get(step.status, "?")

            lines.append(f"  {status_icon} Step {step.id}: {step.description}")
            if step.error:
                lines.append(f"    Error: {step.error}")

        return "\n".join(lines)

    def clear_plan(self) -> None:
        """Clear the current plan."""
        self.current_plan.clear()

    def _next_id(self) -> int:
        """Generate next step ID."""
        self.step_counter += 1
        return self.step_counter

    def _get_step_by_id(self, step_id: int) -> Optional[PlanStep]:
        """Find a step by ID."""
        for step in self.current_plan:
            if step.id == step_id:
                return step
        return None
