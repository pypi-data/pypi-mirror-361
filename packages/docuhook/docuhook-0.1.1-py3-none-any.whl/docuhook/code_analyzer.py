import ast


class DocstringFinder(ast.NodeVisitor):
    def __init__(self):
        self.undocumented_functions = []

    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node):
            self.undocumented_functions.append(node)

        self.generic_visit(node)
