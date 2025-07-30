# ModuBotDiscord

ModuBotDiscord is a modular Discord bot framework based on [ModuBotCore](https://github.com/EnderModuBot/core) and [discord.py](https://discordpy.readthedocs.io/). It enables easy development and extension of Discord bots through a flexible, extensible system.

## Features

- Modular command system
- Extendable with custom commands and views
- Permission and owner checks
- Simple configuration via environment variables

## Installation

The recommended way to install is via [PyPI](https://pypi.org/project/ModuBotDiscord/):

```bash
pip install ModuBotDiscord
```

If you want to start your own bot project, use the [ModuBotDiscord Template](https://github.com/EnderModuBot/discord-template):

```bash
git clone https://github.com/EnderModuBot/discord-template.git
cd discord-template
```

> **Note:**
> This repository contains only the source code of ModuBotDiscord and is not runnable as a bot itself.
> For your own projects, please use the template repository.

## Configuration

Create a `.env` file or set the environment variables:

```dotenv
DISCORD_TOKEN=your_discord_bot_token
DISCORD_OWNER_ID=your_user_id
```

## License

MIT License – see [LICENSE](LICENSE)
