
from collections import Counter
import importlib.util
import posixpath
import sys
import sysconfig

from code_analyzer import analyze_python_code

def classify_import(module, repository_modules):
    """Classify an import as standard library, third-party, or internal."""

    if not module:
        return "unknown"

    top_level_module = module.split(".")[0]

    # Standard-library modules take priority.
    standard_library = getattr(sys, "stdlib_module_names", set())

    if top_level_module in standard_library:
        return "standard_library"

    # Modules defined inside the analyzed repository.
    if top_level_module in repository_modules:
        return "internal"

    # Remaining imports are treated as third-party.
    return "third_party"

def summarize_repository(owner, repo, source_files):
    """Build a repository overview from the Python files analyzed."""

    all_imports = Counter()
    import_categories = {
        "standard_library": Counter(),
        "third_party": Counter(),
        "internal": Counter(),
    }
    repository_modules = set()

    for file_path in source_files:
        if not file_path.endswith(".py"):
            continue

        module_path = file_path[:-3].replace("/", ".")
        parts = module_path.split(".")

    # Register the module name and its parent package names.
        for index in range(len(parts)):
            package_name = ".".join(parts[:index + 1])

            if package_name != "__init__":
                repository_modules.add(parts[index])
                repository_modules.add(package_name)
    total_functions = 0
    total_classes = 0
    file_summaries = []
    folder_counts = Counter()

    for file_path, source_code in source_files.items():
        analysis = analyze_python_code(source_code)

        if "error" in analysis:
            continue

        imports = analysis["imports"]
        functions = analysis["functions"]
        classes = analysis["classes"]

        total_functions += len(functions)
        total_classes += len(classes)

        for item in imports:
            if isinstance(item, str):
                module = item.split(".")[0]
            else:
                module = (item.get("module") or "").split(".")[0]

            if module:
                all_imports[module] += 1
                category = classify_import(module, repository_modules)

                if category in import_categories:
                    import_categories[category][module] += 1

        folder = posixpath.dirname(file_path) or "."
        folder_counts[folder] += 1

        file_summaries.append({
            "path": file_path,
            "imports_count": len(imports),
            "functions_count": len(functions),
            "classes_count": len(classes),
            "functions": [
                item["name"] for item in functions
            ][:10],
            "classes": [
                item["name"] for item in classes
            ][:10],
        })

    common_libraries = {
        "flask": "Flask",
        "django": "Django",
        "fastapi": "FastAPI",
        "requests": "Requests",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "torch": "PyTorch",
        "tensorflow": "TensorFlow",
        "sklearn": "Scikit-learn",
        "networkx": "NetworkX",
        "pytest": "Pytest",
        "sqlalchemy": "SQLAlchemy",
        "numpy": "NumPy",
    }

    detected_libraries = sorted({
        common_libraries.get(module, module)
        for module in import_categories["third_party"]
    })

    entrypoint_candidates = [
        path for path in source_files
        if posixpath.basename(path) in {
            "main.py", "app.py", "run.py", "__main__.py"
        }
    ]

    largest_folders = [
        {"path": folder, "python_files": count}
        for folder, count in folder_counts.most_common(10)
    ]

    return {
        "repository": f"{owner}/{repo}",
        "overview": (
            f"{owner}/{repo} contains "
            f"{len(file_summaries)} analyzable Python files, "
            f"with {total_functions} functions and "
            f"{total_classes} classes."
        ),
        "statistics": {
            "python_files_analyzed": len(file_summaries),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "distinct_imports": len(all_imports),
        },
        "detected_libraries": detected_libraries,
        "import_categories": {
            category: [
                {"name": module, "count": count}
                for module, count in counter.most_common()
            ]
            for category, counter in import_categories.items()
        },
        "common_imports": [
            {"name": name, "count": count}
            for name, count in all_imports.most_common(10)
        ],
        "main_file_candidates": entrypoint_candidates[:10],
        "folders": largest_folders,
        "file_summaries": file_summaries,
        "limitations": (
            "This overview is based on analyzed Python source files. "
            "Detected imports do not necessarily identify installed "
            "dependencies, and candidate entry points are heuristic."
        ),
    }
