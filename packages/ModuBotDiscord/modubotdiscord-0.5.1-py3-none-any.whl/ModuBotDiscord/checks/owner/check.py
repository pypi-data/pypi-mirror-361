import functools
from typing import Awaitable, Callable, TypeVar, Union

from discord import Interaction
from ModuBotDiscord.config import DiscordConfig
from ModuBotDiscord.utils.messages import ErrorType, send_error

T = TypeVar("T", bound=Callable[..., Awaitable[None]])


def check_bot_owner() -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            interaction: Union[Interaction, None] = None

            for arg in args:
                if isinstance(arg, Interaction):
                    interaction = arg
                    break

            if interaction is None:
                interaction = kwargs.get("interaction")

            if interaction is None:
                raise TypeError("No Interaction found for bot owner check.")

            if interaction.user.id != DiscordConfig.OWNER_ID:
                await send_error(
                    interaction,
                    title=ErrorType.ACTION_NOT_ALLOWED,
                    description="You must be the bot owner to use this command.",
                )
                return None
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_guild_owner() -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            interaction: Union[Interaction, None] = None

            for arg in args:
                if isinstance(arg, Interaction):
                    interaction = arg
                    break

            if interaction is None:
                interaction = kwargs.get("interaction")

            if interaction is None:
                raise TypeError("No Interaction found for guild owner check.")

            if (
                not interaction.guild
                or interaction.user.id != interaction.guild.owner_id
            ):
                await send_error(
                    interaction,
                    title=ErrorType.ACTION_NOT_ALLOWED,
                    description="You must be the server owner to use this command.",
                )
                return None
            return await func(*args, **kwargs)

        return wrapper

    return decorator
