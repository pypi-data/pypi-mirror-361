__all__ = [
    "dshell_keyword",
    "dshell_discord_keyword",
    "dshell_commands",
    "dshell_mathematical_operators",
    "dshell_logical_operators",
    "dshell_operators"
]
from typing import Callable
from ..DISCORD_COMMANDS.dshell_channel import *
from ..DISCORD_COMMANDS.dshell_message import *

dshell_keyword: set[str] = {
    'if', 'else', 'elif', 'loop', '#end', 'var', '#loop', '#if', 'sleep'
}


dshell_discord_keyword: set[str] = {
    'embed', '#embed', 'field', 'perm', 'permission', '#perm', '#permission'
}
dshell_commands: dict[str, Callable] = {
    "sm": dshell_send_message,  # send message
    "dm": dshell_delete_message,
    "pm": dshell_purge_message,
    "cc": dshell_create_text_channel,  # create channel
    "dc": dshell_delete_channel,  # delete channel
    "dcs": dshell_delete_channels,
    "uc": dshell_send_message,
    # update channel (aura toutes les modifications possible -> servira à ne faire qu'une commande pour modifier plusieurs chose sur le salon)
    "rc": dshell_send_message  # rename channel
}

dshell_mathematical_operators: dict[str, tuple[Callable, int]] = {
    r"<": (lambda a, b: a < b, 4),
    r"<=": (lambda a, b: a <= b, 4),
    r"=<": (lambda a, b: a <= b, 4),
    r"=": (lambda a, b: a == b, 4),
    r"!=": (lambda a, b: a != b, 4),
    r"=!": (lambda a, b: a != b, 4),
    r">": (lambda a, b: a > b, 4),
    r">=": (lambda a, b: a >= b, 4),
    r"=>": (lambda a, b: a >= b, 4),

    r".": (lambda a, b: a.b, 9),
    r"->": (lambda a: a.at, 10),  # équivalent à l'appel .at(key)

    r"+": (lambda a, b: a + b, 6),
    r"-": (lambda a, b=None: -a if b is None else a - b, 6),
    # attention : ambiguïté entre unaire et binaire à traiter dans ton parseur
    r"**": (lambda a, b: a ** b, 8),
    r"*": (lambda a, b: a * b, 7),
    r"%": (lambda a, b: a % b, 7),
    r"//": (lambda a, b: a // b, 7),
    r"/": (lambda a, b: a / b, 7),
}

dshell_logical_operators: dict[str, tuple[Callable, int]] = {

    r"and": (lambda a, b: bool(a and b), 2),
    r"&": (lambda a, b: a & b, 2),
    r"or": (lambda a, b: bool(a or b), 1),
    r"|": (lambda a, b: a | b, 1),
    r"in": (lambda a, b: a in b, 4),
    r"not": (lambda a: not a, 3),

}

dshell_operators: dict[str, tuple[Callable, int]] = dshell_logical_operators.copy()
dshell_operators.update(dshell_mathematical_operators)



'''
C_create_var = "var"
    C_obligate_var = "ovar" # rend obligatoire les variables

    # guild
    C_create_channel = "cc"
    C_create_voice_channel = "cvc"
    C_create_forum_channel = "cfc"
    C_create_category = "cca"
    C_create_role = "cr"

    C_delete_channel = "dc"
    C_delete_category = "dca"
    C_delete_role = "dr"

    C_edit_channel = "ec"
    C_edit_voice_channel = "evc"
    C_edit_forum_channel = "efc"
    C_edit_category = "eca"
    C_edit_role = "er"
    C_edit_guild = "eg"

    # forum
    C_edit_ForumTag = "eft"
    C_create_thread = "ct"
    C_delete_tread = "dt"

    # member
    C_edit_nickname = "en"
    C_ban_member = "bm"
    C_unban_member = "um"
    C_kick_member = "km"
    C_timeout_member = "tm"
    C_move_member = "mm"
    C_add_roles = "ar"
    C_remove_roles = "rr"

    # message
    C_send_message = "sm"
    C_respond_message = "rm"
    C_edit_message = "em"
    C_send_user_message = "sum"
    C_delete_message = "dm"
    C_purge_message = "pm"
    C_create_embed = "e"
    C_regex = "regex"
    C_add_emoji = "ae"
    C_remove_emoji = "re"
    C_clear_emoji = "ce"
    C_remove_reaction = "rre"

    # bouton
    C_create_button = "b"'''
