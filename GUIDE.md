# Developing a Machine Colony bot

Developing a MC bot is pretty easy. This guide will walk you through creating a simple bot. By the end you'll know all you need to build more sophisticated bots.

Here we'll use Python but other languages will be supported soon.

## Installing the command line tools

First, you'll want the Machine Colony command line tools. They can be installed via `pip`:

    pip install mc-cli

This gives you access to the `mc` command in your terminal.

You'll first need to authenticate with:

    mc auth

## Bot architecture

A MC bot basically consists of a `botfile.json` which specifies attributes of the bot and the code that determines what it does.

So first create a directory to house these files:

    mkdir my_bot

Let's create `botfile.json`:

    touch my_bot/botfile.json

And then open it up in your favorite editor.

### `botfile.json`

The `botfile.json` is required for a bot and specifies what Machine Colony needs to know to manage and run it.

```js
{
    "name": "my_bot",           // name of this bot type
    "version": "0.0.1",         // version number of this bot type
    "privacy": "public",        // who can access the bot
    "max_instances": 1,         // maximum number of instances can be created from the bot
    "test_data": {              // data to use when testing this bot (explained further below)
        "foo": "bar"
    },
    "sdk_lang": "python",       // language the bot is written in
    "source_dir": "src",        // which directory, relative to this botfile, the bot's source code is in
    "main_file": "main_module", // which file defines the bot's behavior (explained further below)
    "run_mode": "event",        // when to run the bot, "event"->in response to webhooks or "scheduled"->on a regular interval
    "default_interval": 5       // interval to run the bot, in seconds (only valid for "scheduled" run mode)
}
```

### Defining the bot's behavior

In the `botfile` above we said the source directory is called `src` and that the main file is called `main_module`, so let's create those.

    mkdir my_bot/src
    touch my_bot/src/main_module.py

Then open up `my_bot/src/main_module.py` in your favorite editor.

In this file we'll define a function called `main_handler`. When the bot is called, Machine Colony will call this function.

`main_handler` takes one parameter: the data that is passed to the bot.

This bot will be really simple: it will just output the data that it receives:

```python
def main_handler(ctx):
    return ctx
```

When a bot is called, such as via a webhook, JSON data can be posted to it in with the following format:

```js
{
    "data": {
        "some_key": "some_value"
    },
    "webhook": "http://some.site/to/post/output/to" // optional webhook
}
```

The values at the `data` key is what is passed in at the `data` key in the `ctx` parameter to `main_handler`.

For example, if the example JSON above was sent to the bot, `ctx` would equal `{"data": {"some_key": "some_value"}, "user": { (user data) }}`.

## Testing the bot

When developing a bot, you will often want to test it check that it's functioning properly.

You can use the Machine Colony command line tools to easily test your bot:

    mc bot test my_bot

This uploads your bot to Machine Colony and gives it the test data specified in your `botfile.json`.

If an exception occurs while running your bot, you'll be informed and get a traceback.

Print statements are also captured and returned at the `output` key in the bot's output.

Finally, the actual return value from your bot is stored at the `result` key in the bot's output.

For example, if we define the bot's main handler as:

```python
def main_handler(data):
    print('hello')
    return data
```

And keep our `botfile.json` the same (that is, using the same `test_data` from before), the bot will POST the following to the specified webhook (if there is one):

```json
{
    "output": ["hello"],
    "result": {
        "foo": "bar"
    }
}
```

## Uploading the bot

When you're finished developing your bot, you can upload it to Machine Colony using the command line tools:

    mc bot define my_bot

## Creating a bot instance

Now that you've defined a new bot type, you can create a new instance using the command line tools:

    mc bot create my_bot

That's it!