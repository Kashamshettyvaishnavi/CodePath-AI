
import ast


def analyze_python_code(source_code):
    """
    Analyze Python source code without executing it.
    Extract imports, functions, classes, and function parameters.
    """

    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        return {
            "error": f"Invalid Python syntax: {error}"
        }

    imports = []
    functions = []
    classes = []

    for node in ast.walk(tree):

        # Find import statements
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            imports.append({
                "module": node.module,
                "names": [alias.name for alias in node.names]
            })

        # Find function definitions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "parameters": [
                    argument.arg
                    for argument in node.args.args
                ]
            })

        # Find class definitions
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno
            })

    return {
        "imports": imports,
        "functions": functions,
        "classes": classes
    }