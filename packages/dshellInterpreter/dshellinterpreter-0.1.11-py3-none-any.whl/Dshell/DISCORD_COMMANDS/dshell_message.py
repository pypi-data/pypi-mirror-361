from discord import Embed
from discord.abc import GuildChannel

__all__ = [
    'dshell_send_message',
    'dshell_delete_message',
    'dshell_purge_message'
]


async def dshell_send_message(ctx: GuildChannel, message=None, delete=None, channel=None, embeds=None, embed=None):
    from .._DshellParser.ast_nodes import ListNode
    """
    Sends a message on Discord
    """
    channel_to_send = ctx if channel is None else ctx.guild.get_channel(channel)

    if channel_to_send is None:
        raise Exception(f'Channel {channel} not found!')

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    if embed is not None and isinstance(embed, Embed):
        embeds.add(embed)

    sended_message = await channel_to_send.send(message,
                                                delete_after=delete,
                                                embeds=embeds)

    return sended_message.id


async def dshell_delete_message(ctx: GuildChannel, message, reason=None, delay=0):
    """
    Deletes a message
    """

    delete_message = ctx.get_partial_message(message)  # builds a reference to the message (even if it doesn't exist)

    if delay > 3600:
        raise Exception(f'The message deletion delay is too long! ({delay} seconds)')

    await delete_message.delete(delay=delay, reason=reason)


async def dshell_purge_message(ctx: GuildChannel, message_number, channel=None, reason=None):
    """
    Purges messages from a channel
    """

    purge_channel = ctx if channel is None else ctx.guild.get_channel(channel)

    if purge_channel is None:
        raise Exception(f"Channel {channel} to purge not found!")

    await purge_channel.purge(limit=message_number, reason=reason)
