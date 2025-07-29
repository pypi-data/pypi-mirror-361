import click
from adxp_cli.agent.cli import agent
from adxp_cli.auth.cli import auth
from adxp_cli.model.cli import model


@click.group()
def cli():
    """Command-line interface for AIP server management."""
    pass


cli.add_command(auth)
cli.add_command(agent)
cli.add_command(model)


if __name__ == "__main__":
    cli()
