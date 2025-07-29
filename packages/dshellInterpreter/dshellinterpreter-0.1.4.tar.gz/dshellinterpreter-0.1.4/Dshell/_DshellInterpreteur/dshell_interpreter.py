from asyncio import sleep
from re import findall
from typing import TypeVar, Union, Any, Optional, Callable

from discord import AutoShardedBot, Embed, Colour, PermissionOverwrite, Permissions
from discord.abc import GuildChannel, PrivateChannel

from .._DshellTokenizer.dshell_keywords import *
from .._DshellParser.ast_nodes import *
from .._DshellParser.dshell_parser import parse
from .._DshellParser.dshell_parser import to_postfix, print_ast
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from .._DshellTokenizer.dshell_token_type import Token
from .._DshellTokenizer.dshell_tokenizer import DshellTokenizer

All_nodes = TypeVar('All_nodes', IfNode, LoopNode, ElseNode, ElifNode, ArgsCommandNode, VarNode, IdentOperationNode)
context = TypeVar('context', AutoShardedBot, GuildChannel, PrivateChannel)


class DshellInterpreteur:

    def __init__(self, ast_or_code: Union[list[All_nodes], str], ctx: context, debug: bool = False):
        """
        Interpreter Dshell code or AST.
        """
        self.ast: list[ASTNode] = parse(DshellTokenizer(ast_or_code).start(), StartNode([]))[0]
        self.env: dict[str, Any] = {}
        self.ctx: context = ctx
        if debug:
            print_ast(self.ast)

    async def execute(self, ast: Optional[list[All_nodes]] = None):
        """
        Execute l'arbre syntaxique.
        """
        if ast is None:
            ast = self.ast

        for node in ast:

            if isinstance(node, StartNode):
                await self.execute(node.body)

            if isinstance(node, CommandNode):
                self.env['__cr__'] = await call_function(dshell_commands[node.name], node.body, self)

            elif isinstance(node, IfNode):
                elif_valid = False
                if eval_expression(node.condition, self):
                    await self.execute(node.body)
                    return
                elif node.elif_nodes:

                    for i in node.elif_nodes:
                        if eval_expression(i.condition, self):
                            await self.execute(i.body)
                            elif_valid = True
                            break

                if not elif_valid and node.else_body is not None:
                    await self.execute(node.else_body.body)

            elif isinstance(node, LoopNode):
                self.env[node.variable.name.value] = 0
                for i in DshellIterator(eval_expression(node.variable.body, self)):
                    self.env[node.variable.name.value] = i
                    await self.execute(node.body)

            elif isinstance(node, VarNode):

                first_node = node.body[0]
                if isinstance(first_node, IfNode):
                    self.env[node.name.value] = eval_expression_inline(first_node, self)

                elif isinstance(first_node, EmbedNode):
                    self.env[node.name.value] = build_embed(first_node.body, first_node.fields, self)

                elif isinstance(first_node, PermissionNode):
                    self.env[node.name.value] = build_permission(first_node.body, self)

                else:
                    self.env[node.name.value] = eval_expression(node.body, self)

            elif isinstance(node, IdentOperationNode):
                function = self.eval_data_token(node.function)
                listNode = self.eval_data_token(node.ident)
                if hasattr(listNode, function):
                    getattr(listNode, function)(self.eval_data_token(node.args))

            elif isinstance(node, SleepNode):
                sleep_time = eval_expression(node.body, self)
                if sleep_time > 3600:
                    raise Exception(f'Le temps maximal de sommeil est de 3600 secondes !')
                elif sleep_time < 1:
                    raise Exception(f'Le temps minimal de sommeil est de 1 seconde !')

                await sleep(sleep_time)


            elif isinstance(node, EndNode):
                raise RuntimeError(f"Execution interromput -> #end atteint")

    def eval_data_token(self, token: Token):
        """
        Evalue les tokens de data
        """

        if not hasattr(token, 'type'):
            return token

        if token.type in (DTT.INT, DTT.MENTION):
            return int(token.value)
        elif token.type == DTT.FLOAT:
            return float(token.value)
        elif token.type == DTT.BOOL:
            return token.value.lower() == "true"
        elif token.type == DTT.NONE:
            return None
        elif token.type == DTT.LIST:
            return ListNode(
                [self.eval_data_token(tok) for tok in token.value])  # token.value contient déjà une liste de Token
        elif token.type == DTT.IDENT:
            if token.value in self.env.keys():
                return self.env[token.value]
            return token.value
        elif token.type == DTT.CALL_ARGS:
            return (self.eval_data_token(tok) for tok in token.value)
        elif token.type == DTT.STR:
            for match in findall(rf"\$({'|'.join(self.env.keys())})", token.value):
                token.value = token.value.replace('$' + match, str(self.env[match]))
            return token.value
        else:
            return token.value  # fallback


def eval_expression_inline(if_node: IfNode, interpreter: DshellInterpreteur) -> Token:
    """
    Evalue une expression en ligne des variables
    """
    if eval_expression(if_node.condition, interpreter):
        return eval_expression(if_node.body, interpreter)
    else:
        return eval_expression(if_node.else_body.body, interpreter)


def eval_expression(tokens: list[Token], interpreter: DshellInterpreteur) -> Any:
    """
    Evalue une expressions arithmétique et logique et renvoie son résultat. Cela peut-être un booléen, un entier, un flottant, une chaîne de caractère ou une liste
    """
    postfix = to_postfix(tokens)
    stack = []

    for token in postfix:

        if token.type in {DTT.INT, DTT.FLOAT, DTT.BOOL, DTT.STR, DTT.LIST, DTT.IDENT}:
            stack.append(interpreter.eval_data_token(token))

        elif token.type in (DTT.MATHS_OPERATOR, DTT.LOGIC_OPERATOR):
            op = token.value

            if op == "not":
                a = stack.pop()
                result = dshell_operators[op][0](a)

            else:
                b = stack.pop()
                a = stack.pop()
                result = dshell_operators[op][0](a, b)

            stack.append(result)

        else:
            raise SyntaxError(f"Token inattendu en condition: {token}")

    if len(stack) != 1:
        raise SyntaxError("Condition mal formée")

    return stack[0]


async def call_function(function: Callable, args: ArgsCommandNode, interpreter: DshellInterpreteur):
    """
    Appelle une fonction avec évaluation des arguments Dshell en valeurs Python
    """
    reformatted = regroupe_commandes(args.body, interpreter)

    # conversion des args en valeurs Python
    absolute_args = reformatted.pop('*', list())

    reformatted: dict[str, Token]  # ne sert à rien, juste à indiquer ce qu'il contient dorénanvant

    absolute_args.insert(0, interpreter.ctx)
    keyword_args = {
        key: value for key, value in reformatted.items()
    }
    return await function(*absolute_args, **keyword_args)


def regroupe_commandes(body: list[Token], interpreter: DshellInterpreteur) -> dict[Union[str, Token], list[Any]]:
    """
    Regroupe les arguments de la commande sous la forme d'un dictionnaire python.
    Sachant que l'on peut spécifier le paramètre que l'on souhaite passer via -- suivit du nom du paramètre. Mais ce n'est pas obligatoire !
    Les paramètres non obligatoire seront stocké dans une liste sous la forme de tokens avec comme clé '*'.
    Les autres ayant été spécifié via un séparateur, ils seront sous la forme d'une liste de tokens avec comme clé le token IDENT qui suivra le séparateur pour chaque argument.
    """
    tokens = {'*': []}  # les tokens à renvoyer
    current_arg = '*'  # les clés des arguments sont les types auquels ils appartiennent. L'* sert à tous les arguments non explicité par un séparateur et un IDENT
    n = len(body)

    i = 0
    while i < n:
        if body[i].type == DTT.SEPARATOR and body[
            i + 1].type == DTT.IDENT:  # On regarde si c'est un séparateur et si le token suivant est un IDENT
            current_arg = body[i + 1].value  # on change l'argument actuel. Il sera donc impossible de revenir à l'*
            tokens[current_arg] = ''  # on lui crée une paire clé/valeur
            i += 2  # on skip l'IDENT qu'il y a après le séparateur car on vient de le traiter
        else:
            if current_arg == '*':
                tokens[current_arg].append(interpreter.eval_data_token(body[i]))
            else:
                tokens[current_arg] = interpreter.eval_data_token(body[i])  # on ajoute le token à l'argument actuel
            i += 1
    return tokens


def build_embed(body: list[Token], fields: list[FieldEmbedNode], interpreter: DshellInterpreteur) -> Embed:
    """
    Construit un embed à partir des informations de la commande.
    """
    args_main_embed: dict[Union[str, Token], list[Any]] = regroupe_commandes(body, interpreter)
    args_main_embed.pop('*')  # on enlève les paramètres non spécifié pour l'embed
    args_main_embed: dict[str, Token]  # on précise se qu'il contient dorénavant

    args_fields: list[dict[str, Token]] = []
    for field in fields:  # on fait la même chose pour tous les fields
        a = regroupe_commandes(field.body, interpreter)
        a.pop('*')
        a: dict[str, Token]
        args_fields.append(a)

    if 'color' in args_main_embed and isinstance(args_main_embed['color'],
                                                 ListNode):  # si on passe l'argument de la couleur sous la forme d'une liste RGB
        args_main_embed['color'] = Colour.from_rgb(*args_main_embed['color'])

    embed = Embed(**args_main_embed)  # on construit l'embed principal
    for field in args_fields:
        embed.add_field(**field)  # on joute tous les fields

    return embed

def build_permission(body: list[Token], interpreter: DshellInterpreteur) -> PermissionOverwrite:
    """
    Construit un dictionnaire de permissions à partir des informations de la commande.
    """
    args_permissions: dict[Union[str, Token], list[Any]] = regroupe_commandes(body, interpreter)
    args_permissions.pop('*')  # on enlève les paramètres non spécifié pour les permissions
    args_permissions: dict[str, Token]  # on précise se qu'il contient dorénavant

    permissions = PermissionOverwrite()

    for key, value in args_permissions.items():

        if key == 'allowed':
            permissions.update(**PermissionOverwrite.from_pair(Permissions(value), Permissions())._values)

        elif key == 'denied':
            permissions.update(**PermissionOverwrite.from_pair(Permissions(), Permissions(value))._values)

        else:
            permissions.update(**{key: value})

    return permissions


class DshellIterator:
    """
    Utilisé pour transformer n'importe quoi en un iterable
    """

    def __init__(self, data):
        if isinstance(data, ListNode):
            self.data = data
        else:
            self.data = data if isinstance(data, (str, list)) else range(int(data))
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):

        if self.current >= len(self.data):
            self.current = 0
            raise StopIteration

        value = self.data[self.current]
        self.current += 1
        return value
