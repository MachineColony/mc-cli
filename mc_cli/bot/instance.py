from mc_cli.api import API


def create(name, **params):
    """create an instance of the bot of type `name`"""
    params['name'] = name
    return API().post('/botinstances', {'bot_instance': params}).json()


def delete(id):
    """delete a bot instance with the specified id"""
    return API().delete('/botinstances/{}'.format(id))


def call(webhook_key, data, webhook=None):
    """call a bot with the specified webhook key, sending the specified data"""
    data = {
        'data': data
    }
    if webhook is not None:
        data['webhook'] = webhook
    return API().hook(webhook_key, data)
