import logging
import warnings
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, List, Optional, TypeVar, Union

import discord
from discord import Embed, Interaction
from discord.utils import MISSING, _MissingSentinel
from ModuBotDiscord.checks.owner import check_bot_owner as _check_bot_owner_new
from ModuBotDiscord.checks.owner import check_guild_owner as _check_guild_owner_new
from ModuBotDiscord.checks.permissions import (
    check_bot_permission as _check_bot_permission_new,
)
from ModuBotDiscord.checks.permissions import check_permission as _check_permission_new
from ModuBotDiscord.utils.messages import send_error as _send_error_new
from ModuBotDiscord.utils.messages import send_message as _send_message_new

from ..enums import PermissionEnum

T = TypeVar("T", bound=Callable[..., Awaitable[None]])

logger = logging.getLogger(__name__)


async def send_message(
    interaction: Interaction,
    content: Optional[str] = None,
    msg: Optional[str] = None,
    *,
    embed: Union[Embed, _MissingSentinel] = MISSING,
    embeds: Union[List[Embed], _MissingSentinel] = MISSING,
    file: Union[discord.File, _MissingSentinel] = MISSING,
    files: Union[List[discord.File], _MissingSentinel] = MISSING,
    view: Union[discord.ui.View, _MissingSentinel] = MISSING,
    tts: bool = False,
    ephemeral: bool = False,
    allowed_mentions: Union[discord.AllowedMentions, _MissingSentinel] = MISSING,
    suppress_embeds: bool = False,
    silent: bool = False,
    delete_after: Optional[float] = None,
    poll: Union[discord.Poll, _MissingSentinel] = MISSING,
) -> Optional[
    Union[
        discord.interactions.InteractionMessage, discord.webhook.async_.WebhookMessage
    ]
]:
    warnings.warn(
        "`ModuBotDiscord.commands.send_message` is deprecated, use `ModuBotDiscord.utils.messages.send_message` instead",
        DeprecationWarning,
        stacklevel=2,
    )

    if msg is not None:
        warnings.warn(
            "`msg` is deprecated, use `content` instead",
            DeprecationWarning,
            stacklevel=2,
        )

        if content is None:
            content = msg

    return await _send_message_new(
        interaction=interaction,
        content=content,
        embed=embed,
        embeds=embeds,
        file=file,
        files=files,
        view=view,
        tts=tts,
        ephemeral=ephemeral,
        allowed_mentions=allowed_mentions,
        suppress_embeds=suppress_embeds,
        silent=silent,
        delete_after=delete_after,
        poll=poll,
    )


async def send_error(
    interaction: Interaction,
    title: str = "⚠️ An error occurred",
    description: Optional[str] = None,
    msg: Optional[str] = None,
) -> None:
    warnings.warn(
        "`ModuBotDiscord.commands.send_error` is deprecated, use `ModuBotDiscord.utils.messages.send_error` instead",
        DeprecationWarning,
        stacklevel=2,
    )

    if msg is not None:
        warnings.warn(
            "`msg` is deprecated, use `title` or `description` instead",
            DeprecationWarning,
            stacklevel=2,
        )
        if description is None:
            description = msg
        else:
            title = msg

    await _send_error_new(interaction=interaction, title=title, description=description)


def check_permission(*permissions: PermissionEnum) -> Callable[[T], T]:
    warnings.warn(
        "`ModuBotDiscord.commands.check_permission` is deprecated, use `ModuBotDiscord.checks.permissions.check_permission` instead",
        DeprecationWarning,
        stacklevel=2,
    )

    return _check_permission_new(*permissions)


def check_bot_permission(*permissions: PermissionEnum) -> Callable[[T], T]:
    warnings.warn(
        "`ModuBotDiscord.commands.check_bot_permission` is deprecated, use `ModuBotDiscord.checks.permissions.check_bot_permission` instead",
        DeprecationWarning,
        stacklevel=2,
    )

    return _check_bot_permission_new(*permissions)


def check_bot_owner() -> Callable[[T], T]:
    warnings.warn(
        "`ModuBotDiscord.commands.check_bot_owner` is deprecated, use `ModuBotDiscord.checks.owner.check_bot_owner` instead",
        DeprecationWarning,
        stacklevel=2,
    )

    return _check_bot_owner_new()


def check_guild_owner() -> Callable[[T], T]:
    warnings.warn(
        "`ModuBotDiscord.commands.check_guild_owner` is deprecated, use `ModuBotDiscord.checks.owner.check_guild_owner` instead",
        DeprecationWarning,
        stacklevel=2,
    )

    return _check_guild_owner_new()


class BaseCommand(ABC):
    @abstractmethod
    async def register(self, bot: "ModuBotDiscord"):
        pass
