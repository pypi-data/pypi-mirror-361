from typing import Optional, Any

from .._DshellTokenizer.dshell_token_type import Token

__all__ = [
    'ASTNode',
    'StartNode',
    'ElseNode',
    'ElifNode',
    'IfNode',
    'LoopNode',
    'ArgsCommandNode',
    'CommandNode',
    'VarNode',
    'EndNode',
    'FieldEmbedNode',
    'EmbedNode',
    'SleepNode',
    'IdentOperationNode',
    'ListNode',
    'PermissionNode'
]


class ASTNode:
    pass


class StartNode(ASTNode):
    def __init__(self, body: list):
        self.body = body

    def __repr__(self):
        return f"<Command> - {self.body}"


class ElseNode(ASTNode):
    def __init__(self, body: list[Token]):
        self.body = body

    def __repr__(self):
        return f"<Else> - {self.body}"


class ElifNode(ASTNode):
    def __init__(self, condition: list[Token], body: list[Token], parent: "IfNode"):
        self.condition = condition
        self.body = body
        self.parent = parent

    def __repr__(self):
        return f"<Elif> - {self.condition} - {self.body}"


class IfNode(ASTNode):
    def __init__(self, condition: list[Token], body: list[Token], elif_nodes: Optional[list[ElifNode]] = None,
                 else_body: Optional[ElseNode] = None):
        self.condition = condition
        self.body = body
        self.elif_nodes = elif_nodes
        self.else_body = else_body

    def __repr__(self):
        return f"<If> - {self.condition} - {self.body} *- {self.elif_nodes} **- {self.else_body}"


class LoopNode(ASTNode):
    def __init__(self, variable: "VarNode", body: list):
        self.variable = variable  # content l'itérable dans son body
        self.body = body

    def __repr__(self):
        return f"<Loop> - {self.variable.name} -> {self.variable.body} *- {self.body}"


class ArgsCommandNode(ASTNode):
    def __init__(self, body: list[Token]):
        self.body: list[Token] = body

    def __repr__(self):
        return f"<Args Command> - {self.body}"


class CommandNode(ASTNode):
    def __init__(self, name: str, body: ArgsCommandNode):
        self.name = name
        self.body = body

    def __repr__(self):
        return f"<{self.name}> - {self.body}"


class VarNode(ASTNode):
    def __init__(self, name: Token, body: list[Token]):
        self.name = name
        self.body = body

    def __repr__(self):
        return f"<VAR> - {self.name} *- {self.body}"


class EndNode(ASTNode):
    def __init__(self):
        pass

    def __repr__(self):
        return f"<END>"


class FieldEmbedNode(ASTNode):
    def __init__(self, body: list[Token]):
        self.body: list[Token] = body

    def __repr__(self):
        return f"<EMBED_FIELD> - {self.body}"


class EmbedNode(ASTNode):
    def __init__(self, body: list[Token], fields: list[FieldEmbedNode]):
        self.body = body
        self.fields = fields

    def __repr__(self):
        return f"<EMBED> - {self.body}"


class PermissionNode(ASTNode):
    def __init__(self, body: list[Token]):
        self.body = body

    def __repr__(self):
        return f"<PERMISSION> - {self.body}"


class SleepNode(ASTNode):
    def __init__(self, body: list[Token]):
        self.body = body

    def __repr__(self):
        return f"<SLEEP> - {self.body}"


class IdentOperationNode(ASTNode):
    """
    Gère les opération sur les idendificateur (appel de fonctions)
    Faire en sorte que l'appel de la fonction renvoie la class associé pour permettre les imbrications. Pas obligatoire en soit si elle renvoie quelque chose
    """

    def __init__(self, ident: Token, function: Token, args: Token):
        self.ident = ident  # content la "class"
        self.function = function  # contient la méthode appelé
        self.args = args  # contient une liste de tokens des arguments passé en paramètre

    def __repr__(self):
        return f"<IDENT OPERATION> - {self.ident}.{self.function}({self.args})"


class ListNode(ASTNode):
    """
    Class iterable permettant de parcourir les listes créé à partir du code Dshell.
    Cette class permet aussi d'intéragir avec la liste via des méthodes spécifique non built-in par python.
    """

    def __init__(self, body: list[Any]):
        self.iterable: list[Any] = body
        self.len_iterable: int = len(body)
        self.iterateur_count: int = 0

    def add(self, value: Any):
        """
        Ajoute un token à la liste
        """
        if self.len_iterable > 10000:
            raise PermissionError('Une liste ne peut dépasser les 10.000 éléments !')

        self.iterable.append(value)
        self.len_iterable += 1

    def remove(self, value: Any, number: int = 1):
        """
        Enlève un ou plusieurs token de la liste
        """
        if number < 1:
            raise Exception(f"Le nombre d'élément à retirer doit-être égale ou supperieur à 1 !")

    def __add__(self, other: "ListNode"):
        for i in other:
            self.add(i)
        return self

    def __iter__(self):
        return self

    def __next__(self):

        if self.iterateur_count >= self.len_iterable:
            self.iterateur_count = 0
            raise StopIteration()

        v = self.iterable[self.iterateur_count]
        self.iterateur_count += 1
        return v

    def __len__(self):
        return self.len_iterable

    def __getitem__(self, item):
        return self.iterable[item]

    def __bool__(self):
        return bool(self.iterable)

    def __repr__(self):
        return f"<LIST> - {self.iterable}"
