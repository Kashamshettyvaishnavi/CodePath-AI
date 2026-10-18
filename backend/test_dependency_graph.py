from dependency_graph import build_dependency_graph, graph_to_dict

files = {
    # Existing test cases
    "app.py": "import auth\n",
    "auth.py": "import database\n",
    "database.py": "def connect():\n    pass\n",
    "utils.py": "def helper():\n    pass\n",

    # Relative import test cases
    "src/flask/__init__.py": "from .ctx import has_app_context\n",
    "src/flask/ctx.py": "def has_app_context():\n    pass\n",
    "src/flask/app.py": "from .ctx import has_app_context\n",

    # Package submodule test case
    "src/flask/json/__init__.py": "from .provider import JSONProvider\n",
    "src/flask/json/provider.py": "class JSONProvider:\n    pass\n",
}

graph = build_dependency_graph(files)
result = graph_to_dict(graph)

print("Nodes:")
for node in result["nodes"]:
    print(node)

print("\nEdges:")
for edge in result["edges"]:
    print(edge)

print("\nTotal files:", graph.number_of_nodes())
print("Total dependencies:", graph.number_of_edges())

# Verify expected dependency relationships.
expected_edges = [
    ("app.py", "auth.py"),
    ("auth.py", "database.py"),
    ("src/flask/__init__.py", "src/flask/ctx.py"),
    ("src/flask/app.py", "src/flask/ctx.py"),
    ("src/flask/json/__init__.py", "src/flask/json/provider.py"),
]

print("\nDependency checks:")
for source, target in expected_edges:
    exists = graph.has_edge(source, target)
    print(f"{source} -> {target}: {'PASS' if exists else 'FAIL'}")


print("\nAmbiguous module test:")

ambiguous_files = {
    "app.py": "import utils\n",
    "src/utils.py": "def helper():\n    pass\n",
    "tests/utils.py": "def test_helper():\n    pass\n",
}

ambiguous_graph = build_dependency_graph(ambiguous_files)

print("app.py dependencies:")
print(sorted(ambiguous_graph.successors("app.py")))