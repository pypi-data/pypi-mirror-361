import logging
from typing import List, Optional, Union

from discord import AllowedMentions, Embed, File, Interaction, Poll
from discord.interactions import InteractionMessage
from discord.ui import View
from discord.utils import MISSING, _MissingSentinel
from discord.webhook.async_ import WebhookMessage

from .enums import ErrorType

logger = logging.getLogger(__name__)


async def send_message(
    interaction: Interaction,
    content: Optional[str] = None,
    *,
    embed: Union[Embed, _MissingSentinel] = MISSING,
    embeds: Union[List[Embed], _MissingSentinel] = MISSING,
    file: Union[File, _MissingSentinel] = MISSING,
    files: Union[List[File], _MissingSentinel] = MISSING,
    view: Union[View, _MissingSentinel] = MISSING,
    tts: bool = False,
    ephemeral: bool = False,
    allowed_mentions: Union[AllowedMentions, _MissingSentinel] = MISSING,
    suppress_embeds: bool = False,
    silent: bool = False,
    delete_after: Optional[float] = None,
    poll: Union[Poll, _MissingSentinel] = MISSING,
) -> Optional[Union[InteractionMessage, WebhookMessage]]:
    if interaction.is_expired():
        logger.warning("Interaction is expired. Skipping send_message().")
        return None

    if interaction.response.is_done():
        return await interaction.followup.send(
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
            poll=poll,
        )

    await interaction.response.send_message(
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

    return await interaction.original_response()


async def send_error(
    interaction: Interaction,
    title: Union[str, ErrorType] = ErrorType.DEFAULT,
    description: Optional[str] = None,
) -> None:

    if isinstance(title, ErrorType):
        title = title.value

    embed: Embed = Embed(title=title, description=description, color=0xFF0000)
    await send_message(interaction, embed=embed, ephemeral=True)
