"""Core I/O operations for SimplePlan project planning."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from .models import ProjectMetadata, ProjectPlan, ProjectStep


class ProjectPlanError(Exception):
    """Base exception for project plan operations."""

    pass


class ProjectPlanNotFoundError(ProjectPlanError):
    """Raised when a project plan file is not found."""

    pass


class ProjectPlanValidationError(ProjectPlanError):
    """Raised when project plan validation fails."""

    pass


class ProjectPlanIO:
    """Handles all project plan I/O operations."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.default_plan_path = Path("project_plan.json")

    def save_project_plan(self, plan: ProjectPlan, path: Optional[Path] = None) -> Path:
        """Save a project plan to disk with proper validation."""
        if path is None:
            path = self.default_plan_path

        try:
            # Update the updated_at timestamp
            plan.updated_at = datetime.now()

            # Validate the plan structure
            validation_errors = plan.validate_dependencies()
            if validation_errors:
                raise ProjectPlanValidationError(
                    f"Validation errors: {', '.join(validation_errors)}"
                )

            # Convert to JSON and save
            plan_dict = plan.model_dump(mode="json")
            path.write_text(json.dumps(plan_dict, indent=2, default=str))

            self.console.print(f"✅ Project plan saved to {path}", style="green")
            return path

        except ValidationError as e:
            raise ProjectPlanValidationError(f"Invalid project plan data: {e}")
        except Exception as e:
            raise ProjectPlanError(f"Failed to save project plan: {e}")

    def load_project_plan(self, path: Optional[Path] = None) -> ProjectPlan:
        """Load a project plan from disk with validation."""
        if path is None:
            path = self.default_plan_path

        if not path.exists():
            raise ProjectPlanNotFoundError(f"Project plan not found: {path}")

        try:
            plan_data = json.loads(path.read_text())
            plan = ProjectPlan.model_validate(plan_data)

            # Validate dependencies
            validation_errors = plan.validate_dependencies()
            if validation_errors:
                self.console.print(
                    f"⚠️  Validation warnings: {', '.join(validation_errors)}",
                    style="yellow",
                )

            return plan

        except json.JSONDecodeError as e:
            raise ProjectPlanValidationError(f"Invalid JSON in project plan: {e}")
        except ValidationError as e:
            raise ProjectPlanValidationError(f"Invalid project plan structure: {e}")
        except Exception as e:
            raise ProjectPlanError(f"Failed to load project plan: {e}")

    def get_status_summary(self, path: Optional[Path] = None) -> str:
        """Get a summary of project plan status."""
        try:
            plan = self.load_project_plan(path)
            completed = sum(1 for step in plan.steps if step.complete)
            total = len(plan.steps)
            percentage = plan.get_completion_percentage()

            return f"{completed}/{total} steps complete ({percentage:.1f}%)"

        except ProjectPlanError:
            return "No project plan found"

    def mark_step_complete(self, step_id: str, path: Optional[Path] = None) -> bool:
        """Mark a step as complete and save the plan."""
        try:
            plan = self.load_project_plan(path)

            # Find the step
            step_found = False
            for step in plan.steps:
                if step.id == step_id:
                    if step.complete:
                        self.console.print(
                            f"⚠️  Step {step_id} is already complete", style="yellow"
                        )
                        return False

                    # Check dependencies
                    completed_step_ids = {s.id for s in plan.steps if s.complete}
                    missing_deps = [
                        dep
                        for dep in step.dependencies
                        if dep not in completed_step_ids
                    ]

                    if missing_deps:
                        self.console.print(
                            f"❌ Cannot complete {step_id}: "
                            f"dependencies not met: {', '.join(missing_deps)}",
                            style="red",
                        )
                        return False

                    step.complete = True
                    step.completed_at = datetime.now()
                    step_found = True
                    break

            if not step_found:
                self.console.print(f"❌ Step {step_id} not found", style="red")
                return False

            # Save the updated plan
            self.save_project_plan(plan, path)
            self.console.print(f"✅ Step {step_id} marked as complete", style="green")
            return True

        except ProjectPlanError as e:
            self.console.print(f"❌ Error completing step: {e}", style="red")
            return False

    def add_step(
        self,
        description: str,
        step_type: str = "task",
        dependencies: Optional[List[str]] = None,
        assigned_to: str = "AI",
        path: Optional[Path] = None,
    ) -> Optional[str]:
        """Add a new step to the project plan."""
        try:
            plan = self.load_project_plan(path)

            # Generate a unique step ID
            existing_ids = {step.id for step in plan.steps}
            step_counter = len(plan.steps) + 1
            step_id = f"STEP-{step_counter:03d}"

            # Ensure uniqueness
            while step_id in existing_ids:
                step_counter += 1
                step_id = f"STEP-{step_counter:03d}"

            # Create the new step
            new_step = ProjectStep(
                id=step_id,
                description=description,
                step_type=step_type,
                dependencies=dependencies or [],
                assigned_to=assigned_to,
            )

            plan.steps.append(new_step)
            self.save_project_plan(plan, path)

            self.console.print(f"✅ Added step {step_id}: {description}", style="green")
            return step_id

        except ProjectPlanError as e:
            self.console.print(f"❌ Error adding step: {e}", style="red")
            return None

    def list_steps(
        self, path: Optional[Path] = None, show_completed: bool = True
    ) -> None:
        """Display all steps in a formatted table."""
        try:
            plan = self.load_project_plan(path)

            if not plan.steps:
                self.console.print("No steps found in project plan", style="yellow")
                return

            table = Table(title=f"Project: {plan.name}")
            table.add_column("Step ID", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Status", style="green")
            table.add_column("Type", style="blue")
            table.add_column("Dependencies", style="yellow")

            for step in plan.steps:
                if not show_completed and step.complete:
                    continue

                status = "✅ Complete" if step.complete else "⏳ Pending"
                deps = ", ".join(step.dependencies) if step.dependencies else "None"

                table.add_row(step.id, step.description, status, step.step_type, deps)

            self.console.print(table)

            # Show summary
            completion_percentage = plan.get_completion_percentage()
            self.console.print(f"\n📊 Progress: {completion_percentage:.1f}% complete")

            # Show next available steps
            next_steps = plan.get_next_available_steps()
            if next_steps:
                self.console.print(
                    f"🎯 Next available steps: "
                    f"{', '.join(step.id for step in next_steps)}"
                )

        except ProjectPlanError as e:
            self.console.print(f"❌ Error listing steps: {e}", style="red")

    def create_project_plan(
        self,
        name: str,
        description: str = "",
        initiator: str = "AI",
        path: Optional[Path] = None,
    ) -> ProjectPlan:
        """Create a new project plan."""
        try:
            project_id = str(uuid.uuid4())[:8]

            metadata = ProjectMetadata(
                initiator=initiator, ai_generated=True, priority="medium"
            )

            plan = ProjectPlan(
                project_id=project_id,
                name=name,
                description=description,
                metadata=metadata,
                steps=[],
            )

            self.save_project_plan(plan, path)
            self.console.print(f"✅ Created new project plan: {name}", style="green")
            return plan

        except Exception as e:
            raise ProjectPlanError(f"Failed to create project plan: {e}")


# Convenience functions for backward compatibility
def save_project_plan(
    plan: Union[ProjectPlan, Dict[str, Any]], path: Optional[Path] = None
) -> Path:
    """Save a project plan to disk."""
    io = ProjectPlanIO()
    if isinstance(plan, dict):
        plan = ProjectPlan.model_validate(plan)
    return io.save_project_plan(plan, path)


def load_project_plan(path: Optional[Path] = None) -> ProjectPlan:
    """Load a project plan from disk."""
    io = ProjectPlanIO()
    return io.load_project_plan(path)


def get_status_summary(path: Optional[Path] = None) -> str:
    """Get a summary of project plan status."""
    io = ProjectPlanIO()
    return io.get_status_summary(path)


def mark_step_complete(step_id: str, path: Optional[Path] = None) -> bool:
    """Mark a step as complete."""
    io = ProjectPlanIO()
    return io.mark_step_complete(step_id, path)
