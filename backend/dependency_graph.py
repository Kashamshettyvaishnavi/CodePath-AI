
import ast
import posixpath
import networkx as nx
from itertools import islice




def extract_imports(source_code):
    """Extract imports, preserving names imported with 'from ... import ...'."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, 0, ()))

        elif isinstance(node, ast.ImportFrom):
            names = tuple(
                alias.name for alias in node.names
                if alias.name != "*"
            )
            imports.append((node.module or "", node.level, names))

    return imports


def resolve_module(module_name, level, file_path):
    """Resolve an import to a repository-relative module path."""
    current_dir = posixpath.dirname(file_path)

    if level > 0:
        package_dir = current_dir

        if level > 1:
            for _ in range(level - 1):
                package_dir = posixpath.dirname(package_dir)

        if module_name:
            target = posixpath.normpath(
                posixpath.join(
                    package_dir, module_name.replace(".", "/")
                )
            )
        else:
            target = posixpath.normpath(package_dir)
    else:
        target = module_name.replace(".", "/")

    return target


def build_dependency_graph(files):
    """Build a graph using resolved modules and imported submodules."""
    graph = nx.DiGraph()

    normalized_files = {
        path.replace("\\", "/"): source
        for path, source in files.items()
        if path.replace("\\", "/").endswith(".py")
    }
    graph.add_nodes_from(normalized_files)

    # Map module paths to their actual Python files.
    module_index = {}

    for file_path in normalized_files:
        stem = file_path[:-3]

        if stem.endswith("/__init__"):
            module_path = stem[:-len("/__init__")]
        else:
            module_path = stem

        module_index.setdefault(module_path, set()).add(file_path)

    def find_candidates(target, level):
        candidates = module_index.get(target, set())

        # Support repository layouts such as src/flask/app.py.
        if not candidates and level == 0:
            suffix = "/" + target
            matches = {
                path
                for module_path, paths in module_index.items()
                if module_path.endswith(suffix)
                for path in paths
            }

            if len(matches) == 1:
                candidates = matches

        return candidates

    for file_path, source_code in normalized_files.items():
        for module_name, level, imported_names in extract_imports(source_code):
            target = resolve_module(module_name, level, file_path)
            base_candidates = find_candidates(target, level)

            # A plain import points to its module.
            if not imported_names:
                candidates = base_candidates

            else:
                candidates = set()

                # Check whether imported names are actual submodules.
                for name in imported_names:
                    submodule_name = (
                        f"{module_name}.{name}" if module_name else name
                    )
                    submodule_target = resolve_module(
                        submodule_name, level, file_path
                    )
                    submodule_candidates = find_candidates(
                        submodule_target, level
                    )

                    if submodule_candidates:
                        candidates.update(submodule_candidates)

                    elif base_candidates:
                        # The name is more likely a symbol exported by
                        # the base module, so depend on that module.
                        candidates.update(base_candidates)

                # For 'from package import *', use the base module.
                if not imported_names and base_candidates:
                    candidates.update(base_candidates)

            for candidate in candidates:
                if candidate != file_path:
                    graph.add_edge(file_path, candidate)

    return graph



def graph_to_dict(graph):
    """Convert the graph into JSON-friendly data."""
    return {
        "nodes": [
            {"id": node}
            for node in graph.nodes
        ],
        "edges": [
            {"source": source, "target": target}
            for source, target in graph.edges
        ]
    }



def find_circular_dependencies(graph):
    """Find a bounded number of short dependency cycles."""
    try:
        cycles = nx.simple_cycles(graph, length_bound=6)
        return list(islice(cycles, 100))
    except Exception as error:
        raise RuntimeError(
            f"Failed to detect circular dependencies: {error}"
        ) from error


def find_circular_dependency_groups(graph):
    """Find groups of files connected through dependency cycles."""
    groups = []

    for component in nx.strongly_connected_components(graph):
        if len(component) > 1:
            groups.append(sorted(component))
        elif len(component) == 1:
            node = next(iter(component))
            if graph.has_edge(node, node):
                groups.append([node])

    return groups



def find_change_impact(graph, changed_file):
    """Find files that may be affected by changing a file."""
    if changed_file not in graph:
        return {
            "changed_file": changed_file,
            "direct_dependents": [],
            "indirect_dependents": [],
            "total_affected": 0,
        }

    # Reverse the graph so edges point from dependencies
    # to the files that import them.
    reverse_graph = graph.reverse(copy=False)

    # Files that directly import the changed file.
    direct_dependents = list(
        reverse_graph.successors(changed_file)
    )

    # All files that may be affected through dependency chains.
    all_affected = nx.descendants(
        reverse_graph, changed_file
    )

    indirect_dependents = sorted(
        all_affected - set(direct_dependents)
    )

    return {
        "changed_file": changed_file,
        "direct_dependents": sorted(direct_dependents),
        "indirect_dependents": indirect_dependents,
        "total_affected": len(all_affected),
    }

print("\nPackage import test:")

package_files = {
    "package.py": "def helper():\n    pass\n",
    "app.py": "from package import helper\n",
    "package/auth.py": "def login():\n    pass\n",
    "client.py": "from package import auth\n",
}

package_graph = build_dependency_graph(package_files)

print("app.py dependencies:", sorted(package_graph.successors("app.py")))
print("client.py dependencies:", sorted(package_graph.successors("client.py")))