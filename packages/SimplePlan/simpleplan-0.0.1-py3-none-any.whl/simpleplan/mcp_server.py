"""MCP Server for SimplePlan - Enables AI systems to manage project plans.

Model Context Protocol integration for AI systems.

Copyright (c) 2025 Bjorn Johnson
Licensed under the MIT License - see LICENSE file for details.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from rich.console import Console

from .project_plan_io import ProjectPlanIO

# Initialize FastMCP server
mcp: FastMCP = FastMCP("simpleplan")
console: Console = Console()


@mcp.tool()
async def create_project_plan(
    name: str,
    description: str = "",
    initiator: str = "AI",
    project_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new project plan for AI-assisted development.

    Args:
        name: Name of the project
        description: Optional description of the project goals
        initiator: Who initiated this project (defaults to "AI")
        project_file: Optional custom path for the project file

    Returns:
        Dictionary with project creation status and details
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None
        plan = io.create_project_plan(name, description, initiator, path)

        return {
            "success": True,
            "message": f"Created project plan: {plan.name}",
            "project_id": plan.project_id,
            "name": plan.name,
            "description": plan.description,
            "file_path": str(io.default_plan_path if path is None else path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create project plan: {e}",
        }


@mcp.tool()
async def get_project_status(project_file: Optional[str] = None) -> Dict[str, Any]:
    """Get current project status and completion percentage.

    Args:
        project_file: Optional path to specific project file

    Returns:
        Dictionary with project status information
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None
        plan = io.load_project_plan(path)

        completed_steps = [step for step in plan.steps if step.complete]
        total_steps = len(plan.steps)
        completion_percentage = plan.get_completion_percentage()

        return {
            "success": True,
            "project_name": plan.name,
            "project_id": plan.project_id,
            "completion_percentage": completion_percentage,
            "completed_steps": len(completed_steps),
            "total_steps": total_steps,
            "status_summary": (
                f"{len(completed_steps)}/{total_steps} steps complete "
                f"({completion_percentage:.1f}%)"
            ),
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get project status: {e}",
        }


@mcp.tool()
async def add_project_step(
    description: str,
    step_type: str = "task",
    dependencies: Optional[List[str]] = None,
    assigned_to: str = "AI",
    project_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new step to the project plan.

    Args:
        description: Description of what this step accomplishes
        step_type: Type of step (task, development, testing, documentation, etc.)
        dependencies: List of step IDs that must be completed first
        assigned_to: Who is assigned to complete this step
        project_file: Optional path to specific project file

    Returns:
        Dictionary with step creation status and details
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None

        step_id = io.add_step(
            description=description,
            step_type=step_type,
            dependencies=dependencies or [],
            assigned_to=assigned_to,
            path=path,
        )

        if step_id:
            return {
                "success": True,
                "step_id": step_id,
                "description": description,
                "step_type": step_type,
                "dependencies": dependencies or [],
                "assigned_to": assigned_to,
                "message": f"Added step {step_id}: {description}",
            }
        else:
            return {
                "success": False,
                "error": "Failed to generate step ID",
                "message": "Could not add step to project plan",
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add step: {e}",
        }


@mcp.tool()
async def complete_step(
    step_id: str, project_file: Optional[str] = None
) -> Dict[str, Any]:
    """Mark a step as complete with dependency validation.

    Args:
        step_id: ID of the step to mark as complete (e.g., "STEP-001")
        project_file: Optional path to specific project file

    Returns:
        Dictionary with completion status and details
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None

        success = io.mark_step_complete(step_id, path)

        if success:
            return {
                "success": True,
                "step_id": step_id,
                "message": f"Step {step_id} marked as complete",
                "completed_at": "now",
            }
        else:
            return {
                "success": False,
                "step_id": step_id,
                "message": (
                    f"Failed to complete step {step_id} - "
                    f"check dependencies or if step exists"
                ),
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error completing step {step_id}: {e}",
        }


@mcp.tool()
async def get_next_steps(project_file: Optional[str] = None) -> Dict[str, Any]:
    """Get available steps that can be worked on next (dependencies satisfied).

    Args:
        project_file: Optional path to specific project file

    Returns:
        Dictionary with available next steps
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None
        plan = io.load_project_plan(path)

        next_steps = plan.get_next_available_steps()

        steps_data = []
        for step in next_steps:
            steps_data.append(
                {
                    "id": step.id,
                    "description": step.description,
                    "step_type": step.step_type,
                    "assigned_to": step.assigned_to,
                    "dependencies": step.dependencies,
                }
            )

        return {
            "success": True,
            "project_name": plan.name,
            "available_steps": steps_data,
            "count": len(next_steps),
            "message": f"Found {len(next_steps)} available steps to work on",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get next steps: {e}",
        }


@mcp.tool()
async def list_all_steps(
    show_completed: bool = True, project_file: Optional[str] = None
) -> Dict[str, Any]:
    """List all steps in the project plan with their status.

    Args:
        show_completed: Whether to include completed steps in the list
        project_file: Optional path to specific project file

    Returns:
        Dictionary with all project steps and their details
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None
        plan = io.load_project_plan(path)

        steps_data = []
        for step in plan.steps:
            if not show_completed and step.complete:
                continue

            steps_data.append(
                {
                    "id": step.id,
                    "description": step.description,
                    "complete": step.complete,
                    "step_type": step.step_type,
                    "assigned_to": step.assigned_to,
                    "dependencies": step.dependencies,
                    "created_at": step.created_at.isoformat()
                    if step.created_at
                    else None,
                    "completed_at": step.completed_at.isoformat()
                    if step.completed_at
                    else None,
                }
            )

        completion_percentage = plan.get_completion_percentage()
        completed_count = sum(1 for step in plan.steps if step.complete)

        return {
            "success": True,
            "project_name": plan.name,
            "project_id": plan.project_id,
            "steps": steps_data,
            "total_steps": len(plan.steps),
            "completed_steps": completed_count,
            "completion_percentage": completion_percentage,
            "summary": (
                f"{completed_count}/{len(plan.steps)} steps complete "
                f"({completion_percentage:.1f}%)"
            ),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to list steps: {e}",
        }


@mcp.tool()
async def validate_project_plan(project_file: Optional[str] = None) -> Dict[str, Any]:
    """Validate the project plan for dependency errors and inconsistencies.

    Args:
        project_file: Optional path to specific project file

    Returns:
        Dictionary with validation results
    """
    try:
        io = ProjectPlanIO(console)
        path = Path(project_file) if project_file else None
        plan = io.load_project_plan(path)

        errors = plan.validate_dependencies()

        return {
            "success": True,
            "project_name": plan.name,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "error_count": len(errors),
            "message": (
                "Project plan is valid"
                if len(errors) == 0
                else f"Found {len(errors)} validation errors"
            ),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to validate project plan: {e}",
        }


# Main server runner
def main():
    """Entry point for SimplePlan MCP Server."""
    # Only log to stderr to avoid interfering with MCP stdin/stdout protocol
    print("🚀 Starting SimplePlan MCP Server...", file=sys.stderr)
    print("📋 Available tools:", file=sys.stderr)
    print("  • create_project_plan - Create new projects", file=sys.stderr)
    print("  • get_project_status - Check project progress", file=sys.stderr)
    print("  • add_project_step - Add new steps", file=sys.stderr)
    print("  • complete_step - Mark steps as done", file=sys.stderr)
    print("  • get_next_steps - Show available work", file=sys.stderr)
    print("  • list_all_steps - Display all steps", file=sys.stderr)
    print("  • validate_project_plan - Check for errors", file=sys.stderr)
    print("\n📡 Server ready for MCP connections...", file=sys.stderr)

    mcp.run()


if __name__ == "__main__":
    main()
