# mc-cli
Command line client and toolkit

## Installation

still under development, so clone this repo, `cd` into it, then:

    pip install --editable .

this makes the `mc` program available. Execute `mc` to see the options.

There is an additional dependency for testing bots: [ngrok](https://ngrok.com/download)

## Configuration

`mc` looks for a JSON configuration file at `~/.mc`. The following are required:

```json
{
    "client_key": "your client key",
    "client_secret": "your client secret",
    "mc_url": "machine colony url",
    "ml_url": "machine colony models url",
    "mc_hooks_url": "machine colony webhook url"
```

You can use `mc auth` to authenticate with the API and automatically have your client key and secret added to your config.
