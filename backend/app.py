from flask import Flask, jsonify, request
from flask_cors import CORS
from code_analyzer import analyze_python_code
from dependency_graph import (
    build_dependency_graph,
    graph_to_dict,
    find_circular_dependencies,
    find_circular_dependency_groups,
    find_change_impact,
)
import requests
import os
import ast
from repository_summary import summarize_repository
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    **(
        {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        if GITHUB_TOKEN
        else {}
    ),
}

app = Flask(__name__)
CORS(app)

def get_python_files(owner, repo):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD"

    response = requests.get(
        api_url,
        params={"recursive": "1"},
        headers=GITHUB_HEADERS,
        timeout=20,
    )

    if response.status_code == 404:
        raise ValueError("Repository not found or inaccessible.")

    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")

        if remaining == "0":
            raise ValueError(
                "GitHub API rate limit exceeded. "
                f"Reset timestamp: {reset}. "
                "Please wait until the limit resets."
            )

        raise ValueError(
            "GitHub denied the request. "
            f"API response: {response.text[:200]}"
        )

    response.raise_for_status()

    data = response.json()

    if data.get("truncated"):
        raise ValueError(
            "Repository is too large to analyze completely in one request."
        )

    python_files = [
        {
            "path": item["path"],
            "size": item.get("size", 0),
        }
        for item in data.get("tree", [])
        if item.get("type") == "blob"
        and item.get("path", "").endswith(".py")
    ]
    
    return python_files

def get_python_file_content(owner, repo, file_path):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {},
        timeout=20
    )

    if response.status_code == 404:
        raise ValueError(f"File not found: {file_path}")

    response.raise_for_status()
    content = response.text

    if len(content.encode("utf-8")) > 500_000:
        raise ValueError(f"File exceeds the 500 KB limit: {file_path}")

    return content


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to CodePath AI!",
        "status": "running"
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "application": "CodePath AI"
    })

@app.route("/api/message", methods=["GET"])
def get_message():
    return jsonify({
        "message": "React and Flask are connected!",
        "project": "CodePath AI"
    })
@app.route("/api/analyze", methods=["POST"])
def analyze_repository():
    data = request.get_json(silent=True) or {}
    repo_url = data.get("repo_url", "").strip()

    prefix = "https://github.com/"

    if not repo_url.startswith(prefix):
        return jsonify({
            "error": "Please provide a GitHub repository URL."
        }), 400

    parts = repo_url[len(prefix):].strip("/").split("/")

    if len(parts) != 2 or not all(parts):
        return jsonify({
            "error": "URL must follow https://github.com/owner/repository"
        }), 400

    owner, repo = parts

    try:
        python_files = get_python_files(owner, repo)

        return jsonify({
            "repository": f"{owner}/{repo}",
            "python_files_found": len(python_files),
            "python_files": python_files,
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve repository information from GitHub."
        }), 502

@app.route("/api/file-content", methods=["POST"])
def get_file_content():
    data = request.get_json(silent=True) or {}

    owner = data.get("owner", "").strip()
    repo = data.get("repo", "").strip()
    file_path = data.get("file_path", "").strip()

    if not owner or not repo or not file_path:
        return jsonify({
            "error": "Owner, repository, and file path are required."
        }), 400

    try:
        content = get_python_file_content(owner, repo, file_path)

        return jsonify({
            "repository": f"{owner}/{repo}",
            "file_path": file_path,
            "content": content
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve the file from GitHub."
        }), 502
@app.route("/api/analyze-file", methods=["POST"])
def analyze_file():
    data = request.get_json(silent=True) or {}

    owner = data.get("owner", "").strip()
    repo = data.get("repo", "").strip()
    file_path = data.get("file_path", "").strip()

    if not owner or not repo or not file_path:
        return jsonify({
            "error": "Owner, repository, and file path are required."
        }), 400

    if not file_path.endswith(".py"):
        return jsonify({
            "error": "Only Python files can be analyzed."
        }), 400

    try:
        source_code = get_python_file_content(
            owner, repo, file_path
        )

        analysis = analyze_python_code(source_code)

        if "error" in analysis:
            return jsonify(analysis), 422

        return jsonify({
            "repository": f"{owner}/{repo}",
            "file_path": file_path,
            "imports": analysis["imports"],
            "functions": analysis["functions"],
            "classes": analysis["classes"]
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve the file from GitHub."
        }), 502

@app.route("/api/dependency-graph", methods=["POST"])
def dependency_graph_api():
    data = request.get_json(silent=True) or {}

    owner = data.get("owner", "").strip()
    repo = data.get("repo", "").strip()

    if not owner or not repo:
        return jsonify({
            "error": "Repository owner and name are required."
        }), 400

    try:
        # Retrieve the Python files in the repository.
        python_files = get_python_files(owner, repo)

        # Limit the initial graph to 50 files.
        # Limit the initial graph to 10 files.
        python_files = [
            file for file in python_files
            if file["size"] <= 500_000
        ][:50]

        # Download source code for each selected file.
        source_files = {}

        for file in python_files:
            path = file["path"]

            try:
                source_files[path] = get_python_file_content(
                    owner, repo, path
                )
            except ValueError:
                # Skip files that cannot be retrieved.
                continue

        # Build and serialize the dependency graph.
        graph = build_dependency_graph(source_files)
        result = graph_to_dict(graph)

        return jsonify({
            "repository": f"{owner}/{repo}",
            "files_analyzed": graph.number_of_nodes(),
            "dependencies_found": graph.number_of_edges(),
            **result
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve repository files from GitHub."
        }), 502

@app.route("/api/circular-dependencies", methods=["POST"])
def circular_dependencies():
    data = request.get_json(silent=True) or {}
    owner = data.get("owner")
    repo = data.get("repo")

    if not owner or not repo:
        return jsonify({
            "error": "Both owner and repo are required."
        }), 400

    try:
        python_files = get_python_files(owner, repo)

        source_files = {}
        for file_info in python_files:
            file_path = file_info["path"]

            if file_info.get("size", 0) > 500_000:
                continue

            try:
                source_files[file_path] = get_python_file_content(
                    owner, repo, file_path
                )
            except (ValueError, requests.RequestException):
                continue

        graph = build_dependency_graph(source_files)
        cycles = find_circular_dependencies(graph)
        dependency_groups = find_circular_dependency_groups(graph)

        return jsonify({
            "repository": f"{owner}/{repo}",
            "files_analyzed": len(source_files),
            "cycles_found": len(cycles),
            "circular_dependencies": cycles,
            "groups_found": len(dependency_groups),
            "circular_dependency_groups": dependency_groups,
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/change-impact", methods=["POST"])
def change_impact():
    data = request.get_json(silent=True) or {}

    owner = data.get("owner")
    repo = data.get("repo")
    changed_file = data.get("changed_file")

    if not owner or not repo or not changed_file:
        return jsonify({
            "error": "owner, repo, and changed_file are required."
        }), 400

    try:
        python_files = get_python_files(owner, repo)
        source_files = {}

        for file_info in python_files:
            file_path = file_info["path"]

            if file_info.get("size", 0) > 500_000:
                continue

            try:
                source_files[file_path] = get_python_file_content(
                    owner, repo, file_path
                )
            except (ValueError, requests.RequestException):
                continue

        graph = build_dependency_graph(source_files)
        result = find_change_impact(graph, changed_file)

        return jsonify({
            "repository": f"{owner}/{repo}",
            "files_analyzed": len(source_files),
            **result,
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/repository-summary", methods=["POST"])
def repository_summary_api():
    data = request.get_json(silent=True) or {}

    owner = data.get("owner", "").strip()
    repo = data.get("repo", "").strip()

    if not owner or not repo:
        return jsonify({
            "error": "Repository owner and name are required."
        }), 400

    try:
        python_files = get_python_files(owner, repo)

        # Bound the initial analysis to avoid excessive API requests.
        selected_files = [
            file for file in python_files
            if file["size"] <= 500_000
        ][:50]

        source_files = {}

        for file in selected_files:
            try:
                source_files[file["path"]] = get_python_file_content(
                    owner, repo, file["path"]
                )
            except ValueError:
                continue

        summary = summarize_repository(
            owner, repo, source_files
        )

        summary["python_files_discovered"] = len(python_files)
        summary["files_selected"] = len(selected_files)

        return jsonify(summary), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve repository information from GitHub."
        }), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)