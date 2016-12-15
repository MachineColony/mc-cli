import os
import sys
import json
import click
import logging
from mc_cli.api import API


conf_path = os.path.expanduser('~/.mc/config.json')

if not os.path.exists(conf_path):
    json.dump({
        'mc_hooks_url': 'https://hooks.machinecolony.com',
        'mc_api_url': 'https://api.machinecolony.com',
        'ml_url': 'https://ml.machinecolony.com'
    }, open(conf_path, 'w'))

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
def init():
    """initialize the default config"""
    if os.path.exists(conf_path) \
        and not click.confirm('A Machine Colony config already exists. Overwrite?'):
        return

    json.dump({
        'mc_hooks_url': 'https://hooks.machinecolony.com',
        'mc_api_url': 'https://api.machinecolony.com',
        'ml_url': 'https://ml.machinecolony.com'
    }, open(conf_path, 'w'))


@cli.command()
@click.argument('email')
@click.password_option()
def auth(email, password):
    """authenticate with Machine Colony"""
    resp = api.post('/cli-config',
                    {'email': email, 'password': password})

    ensure_mc_dir()

    if os.path.exists(conf_path):
        conf = json.load(open(conf_path, 'r'))
        if 'client_secret' in conf and 'client_key' in conf\
            and not click.confirm('Existing client secret and key found in config. Overwrite?'):
                exit('Not overwriting existing client secret and key')
    else:
        conf = {}
    conf.update(resp.json()['data'])
    json.dump(conf, open(conf_path, 'w'), sort_keys=True, indent=4)


def ensure_mc_dir():
    # Ensure main MC directory exists, i.e. before trying to write the config file
    mc_dir = os.path.expanduser('~/.mc')
    if not os.path.exists(mc_dir):
        os.mkdir(mc_dir)
