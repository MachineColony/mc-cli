import os
import sys
import json
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


@cli.command()
@click.argument('email')
@click.password_option()
def auth(email, password):
    resp = api.post('/cli-config',
                    {'email': email, 'password': password})

    conf_path = os.path.expanduser('~/.mc')
    if os.path.exists(conf_path):
        conf = json.load(open(conf_path, 'r'))
        if 'client_secret' in conf and 'client_key' in conf\
            and not click.confirm('Existing client secret and key found in config. Overwrite?'):
                exit('Not overwriting existing client secret and key')
    else:
        conf = {}
    conf.update(resp.json()['data'])
    json.dump(conf, open(conf_path, 'w'), sort_keys=True, indent=4)
