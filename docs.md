The Machine Colony command line interface `mc` allows you to easily use and develop with the Machine Colony service.

`mc` is divided into two main pieces of functionality: managing bots and managing machine learning models.

## Installation

The CLI requires Python 2.7 and can be installed with `pip`:

    pip install mc-cli

This will provide the `mc` command:

    mc

## Initial configuration

`mc` looks for a JSON configuration file located at `~/.mc`.

You can create this file manually, but it's recommended that you start with the default configuration. This can be created by running:

    mc init

The configuration specifies the following urls, which can be overridden if you are running your own instance of Machine Colony:

- `mc_hooks_url`: where webhooks are sent to
- `mc_url`: the Machine Colony API
- `ml_url`: the Machine Colony Machine Learning API

In addition to these options, the configuration file also keeps track of your client key and client secret for authenticated API endpoints.

Again, you can add these manually, but the easier way is to run:

    mc auth

This will walk you through the authorization process.

## Managing bots

Bot management commands are prefixed with `mc bot`, e.g. `mc bot create`.

With Machine Colony, you _define_ a bot _type_, sort of like a template,, which registers its source code, and then you can _create_ bot _instances_ of that type. These instances are what actually go out and execute the bot's code.

### Defining bot types

A bot type can be defined by running the following command and specifying the directory that contains the `botfile.json` and bot's source:

    mc bot define path/to/bot/source

See our [bot development guide](GUIDE.md) for a walkthrough of developing a simple Machine Colony bot.

### Testing bots

As you develop a bot, you'll find that you want to run it to check that it works as you want and debug it if it isn't.

You could define a new bot each time you want to test it, but that gets old quickly.

`mc` provides a command to streamline this process:

    mc bot test path/to/bot/source

This automatically uploads the bot, executes it on test data provided in `botfile.json` (refer to the [bot development guide](GUIDE.md) for an example) and returns the result and all print output.

### Creating a bot instance

A bot instance is created easily, just run the following, specifying the bot type (i.e. the name of the defined bot as specified in the `botfile.json`):

    mc bot create bot_type

The id of the created bot instance will be printed.

### Listing bot instances and bot types

After awhile you may have quite a few bot instances and bot types. `mc` provides this command to list them with their ids.

To list all bot _instances_:

    mc bot list instances

To list all bot _types_:

    mc bot list types

### Deleting a bot instance or bot type

Since bot instances use system resources and thus accumulate fees, you'll probably want to delete those you aren't using anymore. You can do this with:

    mc bot delete instance bot_id

You can similarly delete a bot type (if there are no active instances of it):

    mc bot delete type bot_id

## Managing models

The compliment to Machine Colony bots are machine learning _models_, which learn and perform sophisticated operations that bots can use. They can also be used directly, i.e. without associating them with a bot.

Model management commands are prefixed with `mc model`, e.g. `mc model create`.

### Creating and training a model

When creating a Machine Colony model you need to specify two files:

- a JSON _spec_ file which describes the model you want to create. The only required specification is the model type, e.g.:

```json
{
    "type": "classifier/auto"
}
```

- a JSON _data_ file which includes the data you wish to train the model on, e.g.:

```json
{
    "x": ["cat tiger lion", "lion cat tiger", "tiger cat lion",
          "dog wolf hound", "hound wolf dog", "dog hound wolf"],
    "y": [0,0,0,1,1,1]
}
```

Once you have these two files you can create the model like so:

    mc model create spec.json data.json

You'll be given the model's id. It may take some time to train the model, so it won't necessarily be available for use immediately.

### Using a model

Once your model is finished training, you'll probably want to start sending it data to generate predictions from.

As with creating a model, using a model requires a data JSON file with the input values, e.g.

```json
{
    "x": ["tiger cat lion", "dog wolf hound"]
}
```

You'll also need to know the type (e.g. `classifier/auto`) and the id of the model you want to use.

Then it's just a matter of running:

    mc model evaluate model_type model_id data.json

For example:

    mc model evaluate classifier/auto 51a11a2c-74f7-4fc7-b467-18f534a10d7b data.json

This will output the predictions returned by the model.

### Listing models

To list all of your models:

    mc model list

### Deleting a model

It's very straightforward to delete a model:

    mc model delete model_id
