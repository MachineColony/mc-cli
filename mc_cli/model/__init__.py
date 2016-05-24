import click
from click import echo
from mc_cli.cli import cli, exit, api, logger


@cli.group()
def model():
    pass


@model.command()
@click.option('-n', default=0)
def list(n):
    """list models"""
    data = api.get('/me/models').json()
    n = n if n else len(data)
    for item in data[:n]:
        output = '\t'.join([
            item['guid'],
            item['type']
        ])
        echo(output)
