import os
import json
import uuid
import click
import shutil
import signal
from click import echo
from mc_cli.cli import cli, exit, api, logger
from mc_cli.bot import testing, instance
from multiprocessing.pool import ThreadPool


@cli.group()
def bot():
    pass


@bot.command()
@click.argument('path', type=click.Path())
def define(path):
    """define a new bot type"""
    botfile = os.path.join(path, 'botfile.json')
    if not os.path.exists(botfile):
        exit('No botfile.json found in the specified directory.')

    bot_conf = json.load(open(botfile, 'r'))
    bot_name = bot_conf['name']

    # zip current directory
    zip_file = shutil.make_archive('/tmp/{}'.format(bot_name), 'zip', path)

    # post to upload endpoint
    logger.info('Uploading bot...')
    api.post('/uploads/botfolder', {},
                files={'file1': (os.path.basename(zip_file), open(zip_file, 'rb'))})


@bot.command()
@click.argument('kind', type=click.Choice(['instances', 'types']))
@click.option('-n', default=0)
def list(kind, n):
    """list bot instances or types"""
    if kind == 'instances':
        data = api.get('/me/botinstances').json()
        n = n if n else len(data)
        for item in data[:n]:
            output = '\t'.join([
                item['guid'],
                item['type']
            ])
            echo(output)
    elif kind == 'types':
        data = api.get('/me/bots').json()
        n = n if n else len(data)
        for item in data[:n]:
            output = '\t'.join([
                item['guid'],
                item['name']
            ])
            echo(output)


@bot.command()
@click.argument('type')
@click.option('--config', type=click.File('r'))
def create(type, config):
    """create a new bot instance"""
    if config is not None:
        conf = json.load(config)
    else:
        conf = {}
    resp = instance.create(type, **conf)
    echo(resp['guid'])


@bot.command()
@click.argument('kind', type=click.Choice(['instance', 'type']))
@click.argument('guid')
def delete(kind, guid):
    """delete a bot instance"""
    if kind == 'instance':
        instance.delete(guid)
    elif kind == 'type':
        pass # TODO no delete endpoint, do we want to delete bot types?


@bot.command()
@click.argument('path', type=click.Path())
@click.option('--timeout', default=10)
def test(path, timeout):
    """test a bot
    this deploys the bot as-is,
    executes it once,
    and returns the webhook response.
    """
    port = 8181
    cwd = os.getcwd()
    botfile = os.path.join(cwd, path, 'botfile.json')
    if not os.path.exists(botfile):
        exit('No botfile.json found in current directory.')

    bot_conf = json.load(open(botfile, 'r'))
    bot_name = bot_conf['name']

    if 'test_data' not in bot_conf:
        exit('Please specify the `test_data` to send (in botfile.json)')

    # stash original conf
    temp_file = '/tmp/botfile_{}.json'.format(uuid.uuid4().hex)
    shutil.copyfile(botfile, temp_file)

    # so we don't interfere with production versions
    # TODO we should have an entirely separate endpoint for testing bots
    bot_conf['version'] = '{}_test'.format(bot_conf['version'])

    # setup tunnel to public_url for testing webhook
    public_url = testing.start_tunnel(port)

    # write testing bot conf
    json.dump(bot_conf, open(botfile, 'w'))

    try:
        # zip current directory
        zip_file = shutil.make_archive('/tmp/{}'.format(bot_name), 'zip', cwd)

        # post to upload endpoint
        logger.info('Uploading bot...')
        api.post('/uploads/botfolder', {},
                 params={'overwrite': True},
                 files={'file1': (os.path.basename(zip_file), open(zip_file, 'rb'))})

        # create a bot instance
        logger.info('Creating bot instance...')
        bot_data = instance.create(bot_name)
        bot_webhook_key = bot_data['webhook_key']
        bot_id = bot_data['guid']

        # create webhook endpoint to capture result
        # do it in a separate process
        # juggle the sigint handler to appropriately terminate with
        # KeyboardInterrupt
        sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = ThreadPool(processes=1)
        signal.signal(signal.SIGINT, sigint_handler)
        result = pool.apply_async(testing.await_hook, (port,))

        # call the bot
        logger.info('Calling bot...')
        test_data = bot_conf['test_data']
        instance.call(bot_webhook_key, test_data, webhook=public_url)

        logger.info('Waiting for result...')
        try:
            result = json.loads(result.get(timeout))
            if 'error' in result:
                logger.error('Exception occurred while executing bot:')
                logger.error('{}: {}'.format(
                    result['error']['type'],
                    result['error']['message']))
                logger.error('Traceback:')
                logger.error('\n'.join(result['error']['traceback']))
                if result['output']:
                    logger.error('\nBot output:')
                    logger.error('\n'.join(result['output']))
            else:
                echo(result)
        except KeyboardInterrupt:
            pool.terminate()
        else:
            pool.close()
            pool.join()

        # cleanup
        instance.delete(bot_id)

    # no matter what happens, restore the original conf!
    finally:
        # restore original bot conf
        shutil.move(temp_file, botfile)
        os.remove(zip_file)


