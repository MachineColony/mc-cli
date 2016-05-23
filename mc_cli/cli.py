import sys
import click
import logging
from mc_cli.api import API


api = API()
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def exit(reason):
    click.echo(reason)
    sys.exit(1)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
def cli(verbose):
    if verbose:
        logger.setLevel(logging.INFO)
