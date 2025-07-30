from discord import Member, User, MISSING
from discord.abc import GuildChannel


__all__ = [
    "dshell_ban_member",
    "dshell_unban_member",
    "dshell_kick_member"
]

async def dshell_ban_member(ctx: GuildChannel, member: int, reason: str = MISSING):
    """
    Bans a member from the server.
    """
    banned_member = ctx.guild.get_member(member)

    if not banned_member:
        return 1 # Member not found in the server

    await ctx.guild.ban(banned_member, reason=reason)

    return banned_member.id

async def dshell_unban_member(ctx: GuildChannel, user: int, reason: str = MISSING):
    """
    Unbans a user from the server.
    """
    banned_users = ctx.guild.bans()
    user_to_unban = None

    async for ban_entry in banned_users:
        if ban_entry.user.id == user:
            user_to_unban = ban_entry.user
            break

    if not user_to_unban:
        return 1  # User not found in the banned list

    await ctx.guild.unban(user_to_unban, reason=reason)

    return user_to_unban.id

async def dshell_kick_member(ctx: GuildChannel, member: int, reason: str = MISSING):
    """
    Kicks a member from the server.
    """
    kicked_member = ctx.guild.get_member(member)

    if not kicked_member:
        return 1  # Member not found in the server

    await ctx.guild.kick(kicked_member, reason=reason)

    return kicked_member.id