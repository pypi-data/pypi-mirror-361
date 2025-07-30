"""Command-line interface for SimplePlan."""

from pathlib import Path

import click
from rich.console import Console

from .project_plan_io import ProjectPlanIO

console = Console()


@click.group()
@click.version_option()
def cli():
    """SimplePlan - AI-friendly project planning CLI tool."""
    pass


@cli.command()
@click.option("--name", prompt="Project name", help="Name of the project")
@click.option("--description", default="", help="Description of the project")
@click.option("--initiator", default="AI", help="Who initiated this project")
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
def create(name: str, description: str, initiator: str, plan_file: str):
    """Create a new project plan."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None
        plan = io.create_project_plan(name, description, initiator, path)
        console.print(f"✅ Created project plan: {plan.name} (ID: {plan.project_id})")
    except Exception as e:
        console.print(f"❌ Error creating project plan: {e}", style="red")


@cli.command()
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
def status(plan_file: str):
    """Show project plan status."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None
        summary = io.get_status_summary(path)
        console.print(f"📊 Project Status: {summary}")
    except Exception as e:
        console.print(f"❌ Error getting status: {e}", style="red")


@cli.command()
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
@click.option(
    "--show-completed/--hide-completed", default=True, help="Show completed steps"
)
def list(plan_file: str, show_completed: bool):
    """List all steps in the project plan."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None
        io.list_steps(path, show_completed)
    except Exception as e:
        console.print(f"❌ Error listing steps: {e}", style="red")


@cli.command()
@click.argument("step_id")
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
def complete(step_id: str, plan_file: str):
    """Mark a step as complete."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None
        success = io.mark_step_complete(step_id, path)
        if success:
            console.print(f"✅ Step {step_id} marked as complete")
        else:
            console.print(f"❌ Failed to complete step {step_id}", style="red")
    except Exception as e:
        console.print(f"❌ Error completing step: {e}", style="red")


@cli.command()
@click.option(
    "--description", prompt="Step description", help="Description of the step"
)
@click.option(
    "--type",
    "step_type",
    default="task",
    help="Type of step (task, refactor, testing, etc.)",
)
@click.option(
    "--dependencies", help="Comma-separated list of step IDs this step depends on"
)
@click.option("--assigned-to", default="AI", help="Who is assigned to this step")
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
def add(
    description: str,
    step_type: str,
    dependencies: str,
    assigned_to: str,
    plan_file: str,
):
    """Add a new step to the project plan."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None

        # Parse dependencies
        deps = [dep.strip() for dep in dependencies.split(",")] if dependencies else []

        step_id = io.add_step(description, step_type, deps, assigned_to, path)
        if step_id:
            console.print(f"✅ Added step {step_id}: {description}")
        else:
            console.print("❌ Failed to add step", style="red")
    except Exception as e:
        console.print(f"❌ Error adding step: {e}", style="red")


@cli.command()
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
def next(plan_file: str):
    """Show the next available steps to work on."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None
        plan = io.load_project_plan(path)

        next_steps = plan.get_next_available_steps()
        if next_steps:
            console.print("🎯 Next available steps:")
            for step in next_steps:
                console.print(f"  • {step.id}: {step.description}")
        else:
            console.print("No steps available to work on")
    except Exception as e:
        console.print(f"❌ Error getting next steps: {e}", style="red")


@cli.command()
@click.option(
    "--file", "plan_file", type=click.Path(), help="Path to project plan file"
)
def validate(plan_file: str):
    """Validate the project plan for errors."""
    try:
        io = ProjectPlanIO(console)
        path = Path(plan_file) if plan_file else None
        plan = io.load_project_plan(path)

        errors = plan.validate_dependencies()
        if errors:
            console.print("❌ Validation errors found:", style="red")
            for error in errors:
                console.print(f"  • {error}")
        else:
            console.print("✅ Project plan is valid", style="green")
    except Exception as e:
        console.print(f"❌ Error validating project plan: {e}", style="red")


if __name__ == "__main__":
    cli()
