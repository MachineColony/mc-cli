import json
import click
from click import echo
from mc_cli.cli import cli, api, exit
from mc_cli.api import API

# model API
mapi = API(url_key='ml_url')


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
            item['model_type']
        ])
        echo(output)


@model.command()
@click.argument('spec', type=click.File('r'))
@click.argument('data', type=click.File('r'))
def create(spec, data):
    """create and train a new model.
    training data file must contain `x` and `y` keys if
    using a supervised model or just the raw data if using
    an unsupervised model."""
    spec = json.load(spec)
    if 'type' not in spec:
        exit('You must specify the model type in your model spec.')
    model_type = spec['type']

    data = json.load(data)
    spec['data'] = data

    resp = mapi.post('/{}/create'.format(model_type), spec)
    resp = resp.json()['data']
    echo('{}:{}'.format(resp['model_id'], resp['status']))


@model.command()
@click.argument('type')
@click.argument('guid')
@click.argument('data', type=click.File('r'))
def evaluate(type, guid, data):
    """evaluate some data using the specified model.
    expects at least an `x` key in the data file."""
    data = json.load(data)
    resp = mapi.post('/{}/{}/evaluate'.format(type, guid), {'data': data})
    echo(resp.json()['data']['results'])


@model.command()
@click.argument('guid')
def delete(guid):
    """delete a model"""
    # TODO this is not implemented in the core api yet
    # api.delete('/models/{}'.format(guid))
    echo('not implemented yet')
