import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_confirmation, show_input
from tinybird.tb.modules.feedback_manager import FeedbackManager


def append_file(ctx: RunContext[TinybirdAgentContext], datasource_name: str, fixture_pathname: str) -> str:
    """Append existing fixture to a datasource

    Args:
        datasource_name: Name of the datasource to append fixture to
        fixture_pathname: Path to the fixture file to append

    Returns:
        str: Message indicating the success or failure of the appending
    """
    try:
        ctx.deps.thinking_animation.stop()
        confirmation = show_confirmation(
            title=f"Append fixture {fixture_pathname} to datasource {datasource_name}?",
            skip_confirmation=ctx.deps.dangerously_skip_permissions,
        )

        if confirmation == "review":
            click.echo()
            feedback = show_input(ctx.deps.workspace_name)
            ctx.deps.thinking_animation.start()
            return (
                f"User did not confirm appending {fixture_pathname} fixture and gave the following feedback: {feedback}"
            )

        if confirmation == "cancel":
            ctx.deps.thinking_animation.start()
            return f"User rejected appending {fixture_pathname} fixture. Skip this step"

        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.highlight(message=f"\n» Appending {fixture_pathname} to {datasource_name}..."))
        ctx.deps.append_data(datasource_name=datasource_name, path=fixture_pathname)
        click.echo(FeedbackManager.success(message=f"✓ Data appended to {datasource_name}"))
        ctx.deps.thinking_animation.start()
        return f"Data appended to {datasource_name}"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error appending fixture {fixture_pathname} to {datasource_name}: {e}"


def append_url(ctx: RunContext[TinybirdAgentContext], datasource_name: str, fixture_url: str) -> str:
    """Append existing fixture to a datasource

    Args:
        datasource_name: Name of the datasource to append fixture to
        fixture_url: external url to the fixture file to append

    Returns:
        str: Message indicating the success or failure of the appending
    """
    try:
        ctx.deps.thinking_animation.stop()
        confirmation = show_confirmation(
            title=f"Append URL {fixture_url} to datasource {datasource_name}?",
            skip_confirmation=ctx.deps.dangerously_skip_permissions,
        )

        if confirmation == "review":
            click.echo()
            feedback = show_input(ctx.deps.workspace_name)
            ctx.deps.thinking_animation.start()
            return f"User did not confirm appending URL {fixture_url} and gave the following feedback: {feedback}"

        if confirmation == "cancel":
            ctx.deps.thinking_animation.start()
            return f"User rejected appending URL {fixture_url}. Skip this step"

        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.highlight(message=f"\n» Appending {fixture_url} to {datasource_name}..."))
        ctx.deps.append_data(datasource_name=datasource_name, path=fixture_url)
        click.echo(FeedbackManager.success(message=f"✓ Data appended to {datasource_name}"))
        ctx.deps.thinking_animation.start()
        return f"Data appended to {datasource_name}"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error appending URL {fixture_url} to {datasource_name}: {e}"
