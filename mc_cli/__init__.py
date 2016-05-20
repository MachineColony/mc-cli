import os
import sys
import json
import click
import shutil
from click import echo
from mc_cli.api import API
from mc_cli.bot import testing, instance
from multiprocessing.pool import ThreadPool


api = API()

def exit(reason):
    echo(reason)
    sys.exit(1)


@click.group()
def cli():
    pass


@cli.group()
def bot():
    pass


@bot.command()
def test():
    """test a bot
    this deploys the bot as-is,
    executes it once,
    and returns the webhook response.
    """
    port = 8181
    cwd = os.getcwd()
    botfile = os.path.join(cwd, 'botfile.json')
    if not os.path.exists(botfile):
        exit('No botfile.json found in current directory.')

    bot_conf = json.load(open(botfile, 'r'))
    bot_name = bot_conf['name']

    # stash original conf
    temp_file = '/tmp/botfile_{}.json'.format(hash(frozenset(bot_conf.items())))
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
        echo('Uploading bot...')
        api.post('/uploads/botfolder', {},
                 params={'overwrite': True},
                 files={'file1': (os.path.basename(zip_file), open(zip_file, 'rb'))})

        # create a bot instance
        echo('Creating bot instance...')
        bot_data = instance.create(bot_name)
        bot_webhook_key = bot_data['webhook_key']
        bot_id = bot_data['guid']

        # create webhook endpoint to capture result
        # do it in a separate process
        pool = ThreadPool(processes=1)
        result = pool.apply_async(testing.await_hook, (port,))

        # call the bot
        echo('Calling bot...')
        instance.call(bot_webhook_key, {'webhook': public_url}) # TODO specify data

        print('Waiting for result...')
        echo(result.get())

        # cleanup
        instance.delete(bot_id)

    # no matter what happens, restore the original conf!
    finally:
        # restore original bot conf
        shutil.move(temp_file, botfile)
