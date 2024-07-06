import click

from .config import Config
from .service_manager import ServiceManager


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = ServiceManager(Config())


@cli.command()
@click.argument("service_name")
@click.pass_obj
def start(manager, service_name):
    """Start a specific service"""
    if manager.start_service(service_name):
        click.echo(f"Service {service_name} started successfully.")
    else:
        click.echo(f"Failed to start service {service_name}.")
        exit(1)


@cli.command()
@click.argument("service_name")
@click.pass_obj
def stop(manager, service_name):
    """Stop a specific service"""
    if manager.stop_service(service_name):
        click.echo(f"Service {service_name} stopped successfully.")
    else:
        click.echo(f"Failed to stop service {service_name}.")
        exit(1)


@cli.command()
@click.pass_obj
def start_all(manager):
    """Start all enabled services"""
    manager.start_all_services()
    click.echo("All enabled services have been started.")


@cli.command()
@click.pass_obj
def stop_all(manager):
    """Stop all services"""
    manager.stop_all_services()
    click.echo("All services have been stopped.")


@cli.command()
@click.pass_obj
def status(manager):
    """Show status of all services"""
    statuses = manager.all_services_status()
    for service, status in statuses.items():
        click.echo(f"{service}: {status}")


if __name__ == "__main__":
    cli()
