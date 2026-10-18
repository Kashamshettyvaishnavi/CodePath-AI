
# CodePath AI — Intelligent Codebase Understanding & Change Impact Platform

CodePath AI is a code analysis platform that helps developers understand Python repositories by visualizing file dependencies, identifying circular dependencies, summarizing repository structure, and estimating the impact of code changes.

## Features

- **GitHub Repository Analysis:** Analyze public GitHub repositories and discover Python files.
- **Dependency Graph Visualization:** Explore relationships between Python files.
- **Circular Dependency Detection:** Identify dependency cycles and groups of interconnected files.
- **Change Impact Analysis:** Find direct and indirect dependents of a changed file.
- **Repository Summary:** Summarize functions, classes, imports, and detected libraries.
- **Python File Analysis:** Inspect imports, functions, classes, and function parameters.

## Tech Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, Flask, Flask-CORS |
| Code Analysis | Python AST |
| Graph Analysis | NetworkX |
| External Integration | GitHub REST API |
| HTTP Requests | Requests |
| Configuration | python-dotenv |

## Architecture

```text
User
 |
 v
React + Vite Frontend
 |
 | HTTP / JSON
 v
Flask REST API
 |
 +---- GitHub REST API
 |       |
 |       v
 |   Repository files
 |
 +---- Python AST
 |       |
 |       v
 |   Imports, functions, classes
 |
 +---- NetworkX
         |
         v
     Dependency graph
         |
         +---- Circular dependency detection
         |
         +---- Change impact analysis
         |
         +---- Graph data for visualization
```

## Project Structure

```text
CodePath-AI/
├── backend/
│   ├── app.py
│   ├── code_analyzer.py
│   ├── dependency_graph.py
│   ├── repository_summary.py
│   └── test_*.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── DependencyGraph.css
│   │   ├── dependencyGraph.jsx
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following before running the project:

- Python 3.12 or a compatible Python version
- Node.js and npm
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Kashamshettyvaishnavi/CodePath-AI.git
cd CodePath-AI
```

### 2. Set up the Python backend

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root if you need authenticated GitHub API requests.

```env
GITHUB_TOKEN=your_github_personal_access_token
```

Replace the placeholder with your own token. Never commit `.env` or expose your token publicly.

The application can use unauthenticated GitHub requests when a token is not configured, subject to GitHub's rate limits.

### 4. Start the backend

From the project root, run:

```powershell
python backend\app.py
```

The Flask API runs at:

```text
http://127.0.0.1:5000
```

### 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually:

```text
http://localhost:5173
```

Keep both the frontend and backend running while using the application.

## API Endpoints

The backend exposes endpoints for the following operations:

| Endpoint | Purpose |
|---|---|
| `GET /` | Basic backend response |
| `GET /api/health` | Health check |
| `GET /api/message` | Example API response |
| `POST /api/analyze` | Discover Python files in a GitHub repository |
| `POST /api/file-content` | Retrieve a Python file's contents |
| `POST /api/analyze-file` | Analyze imports, functions, and classes |
| `POST /api/dependency-graph` | Build a file dependency graph |
| `POST /api/repository-summary` | Generate a repository summary |
| `POST /api/circular-dependencies` | Detect circular dependencies |
| `POST /api/change-impact` | Identify potentially affected files |

For POST requests, provide the repository details and any endpoint-specific parameters as JSON. For repository-analysis endpoints, the expected repository fields include `owner` and `repo`; the change-impact endpoint also requires `changed_file`.

## Testing

With the backend running, open another terminal in the project root and run the test scripts individually:

```powershell
python backend\test_api.py
python backend\test_analyzer.py
python backend\test_analyze_file.py
python backend\test_dependency_graph.py
python backend\test_dependency_api.py
python backend\test_repository_summary.py
python backend\test_circular_dependencies.py
python backend\test_change_impact.py
python backend\test_file_content.py
```

These scripts exercise individual API and analysis features. They are standalone scripts rather than a single pytest suite.

## Limitations

- Dependency analysis focuses on Python files and statically detectable imports.
- Dynamically loaded modules and runtime-generated dependencies may not be detected.
- Change-impact results identify potential dependencies, not guaranteed failures.
- Circular-dependency analysis is bounded to keep the analysis manageable.
- GitHub API rate limits apply, particularly when requests are unauthenticated.
- Large repositories may require additional performance optimizations.

## Future Improvements

- Add more comprehensive automated tests.
- Improve import resolution for complex package layouts.
- Add repository caching and analysis performance optimizations.
- Support additional programming languages.
- Add deployment and a live demo.
- Improve visual explanations of dependency paths and change impact.

## Author

**Vaishnavi Kasham Shetty**

GitHub: [@Kashamshettyvaishnavi](https://github.com/Kashamshettyvaishnavi)

---

Built to make codebases easier to understand, explore, and maintain.
