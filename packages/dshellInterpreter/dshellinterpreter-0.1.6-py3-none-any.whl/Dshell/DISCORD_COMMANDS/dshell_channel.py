from asyncio import sleep
from re import search
from typing import Union

from discord import MISSING, PermissionOverwrite, Member, Role
from discord.abc import GuildChannel

__all__ = [
    'dshell_create_text_channel',
    'dshell_delete_channel',
    'dshell_delete_channels'
]


async def dshell_create_text_channel(ctx: GuildChannel, name, category=None, position=MISSING, slowmode=MISSING,
                                     topic=MISSING, nsfw=MISSING,
                                     permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING):
    """
    Crée un salon textuel sur le serveur
    """

    channel_category = ctx.guild.get_channel(category)

    created_channel = await ctx.guild.create_text_channel(name,
                                                          category=channel_category,
                                                          position=position,
                                                          slowmode_delay=slowmode,
                                                          topic=topic,
                                                          nsfw=nsfw,
                                                          overwrites=permission._values)

    return created_channel.id


async def dshell_delete_channel(ctx: GuildChannel, channel=None, reason=None, timeout=0):
    """
    Supprime un salon.
    Possibilité de lui rajouter un temps d'attente avant qu'il ne le supprime (en seconde)
    """

    channel_to_delete = ctx if channel is None else ctx.guild.get_channel(channel)

    if channel_to_delete is None:
        raise Exception(f"Le channel {channel} n'existe pas !")

    await sleep(timeout)

    await channel_to_delete.delete(reason=reason)

    return channel_to_delete.id


async def dshell_delete_channels(ctx: GuildChannel, name=None, regex=None, reason=None):
    """
    Supprime tous les salons ayant le même nom et/ou le même regex.
    Si aucun des deux n'est mis, il supprimera tous les salons comportant le même nom que celui ou a été fait la commande
    """
    for channel in ctx.guild.channels:

        if name is not None and channel.name == str(name):
            await channel.delete(reason=reason)

        elif regex is not None and search(regex, channel.name):
            await channel.delete(reason=reason)
