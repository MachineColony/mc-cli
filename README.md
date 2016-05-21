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
    "auth_token": "your auth token",
    "mc_url": "machine colony url",
    "mc_hooks_url": "machine colony webhook url"
}
```
