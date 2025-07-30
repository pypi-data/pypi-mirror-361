import functools
from typing import Awaitable, Callable, TypeVar, Union

from discord import Interaction
from ModuBotDiscord.utils.messages import ErrorType, send_error

from .enum import Permission

T = TypeVar("T", bound=Callable[..., Awaitable[None]])


def check_permission(*permissions: Permission) -> Callable[[T], T]:
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
                raise ValueError("No Interaction found for user permission check.")

            missing = [
                perm.value
                for perm in permissions
                if not getattr(interaction.user.guild_permissions, perm.value, False)
            ]
            if missing:
                missing_permissions = ", ".join(f"`{m}`" for m in missing)
                await send_error(
                    interaction,
                    title=ErrorType.ACTION_NOT_ALLOWED,
                    description=f"You are missing the following permissions: {missing_permissions}",
                )
                return None
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_bot_permission(*permissions: Permission) -> Callable[[T], T]:
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
                raise ValueError("No Interaction found for bot permission check.")

            if not interaction.guild:
                await send_error(
                    interaction,
                    title=ErrorType.ACTION_NOT_ALLOWED,
                    description="This command can only be used in a server.",
                )
                return None

            bot_permissions = interaction.guild.me.guild_permissions
            missing = [
                perm.value
                for perm in permissions
                if not getattr(bot_permissions, perm.value, False)
            ]
            if missing:
                missing_permissions = ", ".join(f"`{m}`" for m in missing)
                await send_error(
                    interaction,
                    title=ErrorType.ACTION_NOT_ALLOWED,
                    description=f"The bot is missing the following permissions: {missing_permissions}",
                )
                return None

            return await func(*args, **kwargs)

        return wrapper

    return decorator
