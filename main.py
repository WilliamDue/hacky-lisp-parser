from futhark_ffi import Futhark
import numpy as np
import _parser
import re

class Tree:

    to_names = {
        0: "Sexp0",
        1: "Sexp1",
        2: "Sexp2",
        3: "Sexp3",
        4: "Sexp4",
        5: "Sexp5"
    }

    arities = {
        "Sexp0": [1],
        "Sexp1": [0, 0],
        "Sexp2": [1, 1],
        "Sexp3": [1, 0],
        "Sexp4": [0, 0],
        "Sexp5": [0]
    }

    productions = {
        "Sexp0",
        "Sexp1",
        "Sexp2",
        "Sexp3",
        "Sexp4",
        "Sexp5"
    }

    @classmethod
    def get_arity(ctx, node):
        arity = ctx.arities.get(node)

        if arity is None:
            return []

        return arity.copy()


    def __init__(self, node, children = None) -> None:
        self.node = node
        self.children = children
        if children is not None and len(children) == 0:
            self.children = None
    
    def __str__(self) -> str:

        node_str = self.node if self.node in self.productions else f'"{self.node}"'

        if self.children == None:
            return f'Node({node_str})'

        return f'Node({node_str}, [{", ".join(map(str, self.children))}])'
    
    def traverse(self):
        
        result = [self.node]

        if self.children is None:
            return result
        
        for child in self.children:
            result.extend(child.traverse())

        return result

    @classmethod
    def make_tree(ctx, left_parse, tokens):
        named_parse = list(map(ctx.to_names.get, left_parse))
        
        def auxiliary_make(_left_parse):
            node = _left_parse.pop(0)
            arity = ctx.get_arity(node)

            children = []

            for _ in range(arity.pop(0)):
                children.append(Tree(tokens.pop(0)))
            
            for terminals in arity:
                children.append(auxiliary_make(_left_parse))

                for _ in range(terminals):
                    children.append(Tree(tokens.pop(0)))
            
            return Tree(node, children)

        return auxiliary_make(named_parse)


def lexer(string):
    pattern = re.compile(r'(?P<atom>[a-zA-Z0-9_]+)|(?P<lparen>\()|(?P<rparen>\))|(?P<space>\s+)')
    
    atom = 'atom'
    lparen = 'lparen'
    rparen = 'rparen'
    tokens = []
    terminals = []
    start = 0
    end = len(string)

    while start != end:
        match = pattern.search(string, start)

        if match is None:
            return None
        elif match.start() != start:
            return None
        
        groups = match.groupdict()
        
        if groups[atom] is not None:
            terminals.append(atom)
            tokens.append(groups[atom])
        elif groups[lparen] is not None:
            terminals.append(lparen)
            tokens.append(groups[lparen])
        elif groups[rparen] is not None:
            terminals.append(rparen)
            tokens.append(groups[rparen])
        
        start = match.end()

    return tokens, terminals


def terminal_to_index(terminal):
    if terminal == 'atom':
        return 0
    elif terminal == 'lparen':
        return 1
    elif terminal == 'rparen':
        return 2
    return None


def terminals_to_indices(terminals):
    return list(map(terminal_to_index, terminals))


def main():
    code = input('Code: ')
    tokens, terminals = lexer(code)
    indices = np.array(terminals_to_indices(terminals))
    parser = Futhark(_parser)
    left_parse = list(parser.from_futhark(parser.parse(indices)))
    print(left_parse)
    tree = Tree.make_tree(left_parse, tokens)
    print(tree)
    


if __name__ == '__main__':
    main()