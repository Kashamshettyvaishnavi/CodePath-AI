import { useState } from "react";
import "./App.css";
import DependencyGraph from "./dependencyGraph";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [backendMessage, setBackendMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [fileAnalysis, setFileAnalysis] = useState(null);
  const [fileAnalysisLoading, setFileAnalysisLoading] = useState(false);
  const [fileAnalysisError, setFileAnalysisError] = useState("");
  const [dependencyData, setDependencyData] = useState(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphError, setGraphError] = useState("");
  const [summaryData, setSummaryData] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");
  const [circularData, setCircularData] = useState(null);
  const [circularLoading, setCircularLoading] = useState(false);
  const [circularError, setCircularError] = useState("");

  const [impactData, setImpactData] = useState(null);
  const [impactLoading, setImpactLoading] = useState(false);
  const [impactError, setImpactError] = useState("");


  async function handleAnalyze(event) {
    event.preventDefault();

    if (!repoUrl.trim()) {
      setBackendMessage("Please enter a GitHub repository URL.");
      setAnalysisResult(null);
      return;
    }

    try {
      setLoading(true);
      setBackendMessage("");
      setAnalysisResult(null);

      const response = await fetch(
        "http://127.0.0.1:5000/api/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repo_url: repoUrl,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Repository analysis failed.");
      }

      setAnalysisResult(data);
      //console.log("Repository analysis response:", data);
    } catch (error) {
      console.error("Repository analysis error:", error);
      setBackendMessage(error.message);
    } finally {
      setLoading(false);
    }
  }
  async function handleAnalyzeFile(filePath) {
    try {
      setFileAnalysisLoading(true);
      setFileAnalysisError("");
      setFileAnalysis(null);

      const parsedUrl = new URL(repoUrl);

      if (
        parsedUrl.hostname !== "github.com" ||
        parsedUrl.pathname.split("/").filter(Boolean).length !== 2
      ) {
        throw new Error(
          "Please enter a valid GitHub repository URL first."
        );
      }

      const [owner, repo] = parsedUrl.pathname
        .split("/")
        .filter(Boolean);

      const response = await fetch(
        "http://127.0.0.1:5000/api/analyze-file",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            owner,
            repo,
            file_path: filePath,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "File analysis failed.");
      }

      setFileAnalysis(data);
    } catch (error) {
      console.error("File analysis error:", error);
      setFileAnalysisError(error.message);
    } finally {
      setFileAnalysisLoading(false);
    }
  }

  async function handleLoadGraph() {
    try {
      setGraphLoading(true);
      setGraphError("");
      setDependencyData(null);

      const parsedUrl = new URL(repoUrl);

      if (
        parsedUrl.hostname !== "github.com" ||
        parsedUrl.pathname.split("/").filter(Boolean).length !== 2
      ) {
        throw new Error(
          "Please enter a valid GitHub repository URL first."
        );
      }

      const [owner, repo] = parsedUrl.pathname
        .split("/")
        .filter(Boolean);

      const response = await fetch(
        "http://127.0.0.1:5000/api/dependency-graph",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ owner, repo }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to load dependency graph.");
      }

      setDependencyData(data);
    } catch (error) {
      console.error("Dependency graph error:", error);
      setGraphError(error.message);
    } finally {
      setGraphLoading(false);
    }
  }

  async function handleLoadCircularDependencies() {
    if (!repoUrl.trim()) {
      setCircularError("Please enter a GitHub repository URL.");
      return;
    }

    const match = repoUrl.match(
      /github\.com\/([^/]+)\/([^/]+)/
    );

    if (!match) {
      setCircularError("Please enter a valid GitHub repository URL.");
      return;
    }

    const owner = match[1];
    const repo = match[2].replace(/\.git$/, "");

    setCircularLoading(true);
    setCircularError("");
    setCircularData(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/circular-dependencies",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ owner, repo }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Failed to analyze circular dependencies."
        );
      }

      setCircularData(data);
    } catch (error) {
      setCircularError(error.message);
    } finally {
      setCircularLoading(false);
    }
  }

  async function handleLoadChangeImpact(changedFile) {
    const match = repoUrl.match(/github\.com\/([^/]+)\/([^/]+)/);

    if (!match) {
      setImpactError("Please enter a valid GitHub repository URL.");
      return;
    }

    const owner = match[1];
    const repo = match[2].replace(/\.git$/, "");

    setImpactLoading(true);
    setImpactError("");
    setImpactData(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/change-impact",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            owner,
            repo,
            changed_file: changedFile,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Change impact analysis failed.");
      }

      setImpactData(data);
    } catch (error) {
      setImpactError(error.message);
    } finally {
      setImpactLoading(false);
    }
  }


  async function handleLoadSummary() {
    try {
      setSummaryLoading(true);
      setSummaryError("");
      setSummaryData(null);

      const parsedUrl = new URL(repoUrl);
      const parts = parsedUrl.pathname.split("/").filter(Boolean);

      if (
        parsedUrl.hostname !== "github.com" ||
        parts.length !== 2
      ) {
        throw new Error(
          "Please enter a valid GitHub repository URL first."
        );
      }

      const [owner, repo] = parts;

      const response = await fetch(
        "http://127.0.0.1:5000/api/repository-summary",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ owner, repo }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Unable to generate repository summary."
        );
      }

      setSummaryData(data);
    } catch (error) {
      console.error("Repository summary error:", error);
      setSummaryError(error.message);
    } finally {
      setSummaryLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <span className="brand-icon">&lt;/&gt;</span>
          <span>CodePath AI</span>
        </div>

        <span className="nav-label">Codebase Intelligence Platform</span>
      </header>

      <main className="hero">
        <div className="status-badge">
          <span className="status-dot"></span>
          AI-Powered Code Understanding
        </div>

        <h1>
          Understand any codebase.
          <br />
          <span>Navigate code with confidence.</span>
        </h1>

        <p className="description">
          Explore unfamiliar repositories, discover code dependencies,
          understand change impact, and identify relevant tests—all in one place.
        </p>

        <form className="repo-form" onSubmit={handleAnalyze}>
          <label htmlFor="repoUrl">GitHub repository URL</label>

          <div className="input-group">
            <input
              id="repoUrl"
              type="url"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
              required
            />

            <button type="submit">Analyze Repository →</button>
          </div>
        </form>
        {loading && (
          <p className="backend-message">
            Analyzing repository... Please wait.
          </p>
        )}

        {backendMessage && (
          <div className="backend-message error-message">
            {backendMessage}
          </div>
        )}

        {analysisResult && (
          <section className="analysis-results">
            <h2>Repository Analysis Results</h2>

            <div className="result-summary">
              <div className="result-card">
                <span>Repository</span>
                <strong>{analysisResult.repository}</strong>
              </div>

              <div className="result-card">
                <span>Python Files Found</span>
                <strong>{analysisResult.python_files_found}</strong>
              </div>
            </div>

            <h3>Python Files</h3>

            <div className="file-list">
              {analysisResult.python_files.map((file) => (
                <div className="file-item" key={file.path}>
                  <span className="file-name">{file.path}</span>

                  <span className="file-size">
                    {file.size.toLocaleString()} bytes
                  </span>

                  <button
                    type="button"
                    onClick={() => handleAnalyzeFile(file.path)}
                    disabled={fileAnalysisLoading}
                  >
                    Analyze Code
                  </button>
                </div>
              ))}
            </div>
            {fileAnalysisLoading && (
              <p className="backend-message">
                Analyzing Python code... Please wait.
              </p>
            )}

            {fileAnalysisError && (
              <p className="backend-message error-message">
                {fileAnalysisError}
              </p>
            )}

            {fileAnalysis && (
              <section className="file-analysis-results">
                <h3>Code Structure Analysis</h3>

                <p>
                  <strong>Repository:</strong> {fileAnalysis.repository}
                </p>

                <p>
                  <strong>File:</strong> {fileAnalysis.file_path}
                </p>

                <h4>Imports</h4>
                {fileAnalysis.imports.length > 0 ? (
                  <ul>
                    {fileAnalysis.imports.map((item, index) => (
                      <li key={index}>
                        {typeof item === "string"
                          ? item
                          : `${item.module || ""}: ${item.names.join(", ")}`}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No imports found.</p>
                )}

                <h4>Functions</h4>
                {fileAnalysis.functions.length > 0 ? (
                  <ul>
                    {fileAnalysis.functions.map((fn, index) => (
                      <li key={`${fn.name}-${index}`}>
                        <code>{fn.name}({fn.parameters.join(", ")})</code>
                        {" — Line "}
                        {fn.line}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No functions found.</p>
                )}

                <h4>Classes</h4>
                {fileAnalysis.classes.length > 0 ? (
                  <ul>
                    {fileAnalysis.classes.map((cls, index) => (
                      <li key={`${cls.name}-${index}`}>
                        <code>{cls.name}</code>
                        {" — Line "}
                        {cls.line}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No classes found.</p>
                )}
              </section>
            )}
          </section>

        )}

        <section className="summary-section">
          <h2>Repository Overview</h2>

          <p>
            Understand the structure and composition of your repository.
          </p>

          <button
            type="button"
            onClick={handleLoadSummary}
            disabled={summaryLoading || !analysisResult}
          >
            {summaryLoading
              ? "Generating Summary..."
              : "Generate Repository Summary"}
          </button>

          {!analysisResult && (
            <p>Analyze a repository first to generate its summary.</p>
          )}

          {summaryLoading && (
            <p className="backend-message">
              Analyzing repository structure... Please wait.
            </p>
          )}

          {summaryError && (
            <p className="error-message">{summaryError}</p>
          )}

          {summaryData && (
            <div className="summary-results">
              <h3>{summaryData.repository}</h3>
              <p>{summaryData.overview}</p>

              <div className="result-summary">
                <div className="result-card">
                  <span>Files Analyzed</span>
                  <strong>
                    {summaryData.statistics.python_files_analyzed}
                  </strong>
                </div>

                <div className="result-card">
                  <span>Functions</span>
                  <strong>
                    {summaryData.statistics.total_functions}
                  </strong>
                </div>

                <div className="result-card">
                  <span>Classes</span>
                  <strong>
                    {summaryData.statistics.total_classes}
                  </strong>
                </div>

                <div className="result-card">
                  <span>Distinct Imports</span>
                  <strong>
                    {summaryData.statistics.distinct_imports}
                  </strong>
                </div>
              </div>
              <div className="dependency-overview">
                <div className="dependency-card">
                  <h4>Standard Library</h4>
                  <p>
                    {summaryData.import_categories?.standard_library?.length || 0}
                  </p>
                  <span>Unique modules</span>
                </div>

                <div className="dependency-card">
                  <h4>Third-Party Packages</h4>
                  <p>
                    {summaryData.import_categories?.third_party?.length || 0}
                  </p>
                  <span>Unique packages</span>
                </div>

                <div className="dependency-card">
                  <h4>Internal Modules</h4>
                  <p>
                    {summaryData.import_categories?.internal?.length || 0}
                  </p>
                  <span>Unique modules</span>
                </div>
              </div>
              <h3>Standard Library</h3>
              {summaryData.import_categories?.standard_library?.length > 0 ? (
                <ul>
                  {summaryData.import_categories.standard_library.map((module) => (
                    <li key={module.name}>
                      <code>{module.name}</code> — {module.count} imports
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No standard-library imports detected.</p>
              )}

              <h3>Third-Party Packages</h3>
              {summaryData.import_categories?.third_party?.length > 0 ? (
                <ul>
                  {summaryData.import_categories.third_party.map((module) => (
                    <li key={module.name}>
                      <code>{module.name}</code> — {module.count} imports
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No third-party packages detected.</p>
              )}

              <h3>Internal Modules</h3>
              {summaryData.import_categories?.internal?.length > 0 ? (
                <ul>
                  {summaryData.import_categories.internal.map((module) => (
                    <li key={module.name}>
                      <code>{module.name}</code> — {module.count} imports
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No internal modules detected.</p>
              )}

              <h3>Most Common Imports</h3>
              {summaryData.common_imports.length > 0 ? (
                <ul>
                  {summaryData.common_imports.map((item) => (
                    <li key={item.name}>
                      <code>{item.name}</code> — {item.count} occurrences
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No common imports found.</p>
              )}

              <h3>Folders with the Most Python Files</h3>
              {summaryData.folders.length > 0 ? (
                <ul>
                  {summaryData.folders.map((folder) => (
                    <li key={folder.path}>
                      <code>{folder.path}</code> — {folder.python_files} files
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No folders found.</p>
              )}

              <h3>Candidate Entry-Point Files</h3>
              {summaryData.main_file_candidates.length > 0 ? (
                <ul>
                  {summaryData.main_file_candidates.map((file) => (
                    <li key={file}>
                      <code>{file}</code>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No candidate entry points detected.</p>
              )}

              <h3>File Structure Summaries</h3>
              {summaryData.file_summaries.map((file) => (
                <details className="summary-file" key={file.path}>
                  <summary>{file.path}</summary>

                  <p>
                    Imports: {file.imports_count} | Functions:{" "}
                    {file.functions_count} | Classes: {file.classes_count}
                  </p>

                  <p>
                    <strong>Functions:</strong>{" "}
                    {file.functions.length
                      ? file.functions.join(", ")
                      : "None detected"}
                  </p>

                  <p>
                    <strong>Classes:</strong>{" "}
                    {file.classes.length
                      ? file.classes.join(", ")
                      : "None detected"}
                  </p>

                  <button
                    type="button"
                    onClick={() => handleAnalyzeFile(file.path)}
                    disabled={fileAnalysisLoading}
                  >
                    Analyze File
                  </button>
                </details>
              ))}

              <p className="summary-note">
                {summaryData.limitations}
              </p>
            </div>
          )}
        </section>

        <div className="feature-grid">
          <article className="feature-card">
            <div className="feature-icon">⌘</div>
            <h3>Code Structure</h3>
            <p>Discover functions, classes, and imports in your repository.</p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">◎</div>
            <h3>Dependency Mapping</h3>
            <p>Explore relationships between files and code components.</p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">↗</div>
            <h3>Change Impact</h3>
            <p>Identify components that may be affected by code changes.</p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">✓</div>
            <h3>Test Recommendations</h3>
            <p>Find relevant tests to consider when modifying code.</p>
          </article>
        </div>

        <section className="dependency-section">
          <h2>Dependency Mapping</h2>

          <p>
            Explore the import relationships detected between Python files.
          </p>

          <button
            type="button"
            onClick={handleLoadGraph}
            disabled={graphLoading || !analysisResult}
          >
            {graphLoading ? "Building Graph..." : "Generate Dependency Graph"}
          </button>

          {!analysisResult && (
            <p>Analyze a repository first to enable dependency mapping.</p>
          )}

          {graphError && (
            <p className="error-message">{graphError}</p>
          )}

          {dependencyData && (
            <>
              <div className="result-summary">
                <div className="result-card">
                  <span>Files Analyzed</span>
                  <strong>{dependencyData.files_analyzed}</strong>
                </div>

                <div className="result-card">
                  <span>Dependencies Found</span>
                  <strong>{dependencyData.dependencies_found}</strong>
                </div>
              </div>

              {dependencyData.nodes.length > 0 ? (
                <DependencyGraph graphData={dependencyData} />
              ) : (
                <p>No Python files were available to graph.</p>
              )}

              <section className="circular-dependency-section">
                <h2>Circular Dependency Analysis</h2>

                <p>
                  Identify dependency cycles that may make your codebase
                  harder to maintain.
                </p>

                <button
                  onClick={handleLoadCircularDependencies}
                  disabled={circularLoading}
                >
                  {circularLoading
                    ? "Analyzing..."
                    : "Detect Circular Dependencies"}
                </button>

                {circularError && (
                  <p className="error-message">{circularError}</p>
                )}

                {circularData && (
                  <div className="circular-results">
                    <h3>{circularData.repository}</h3>

                    <p>
                      Files analyzed: {circularData.files_analyzed}
                    </p>

                    <p>
                      Cycles found: {circularData.cycles_found}
                    </p>


                    {circularData.groups_found > 0 ? (
                      <div>
                        <h3>Circular Dependency Groups</h3>

                        {circularData.circular_dependency_groups.map((group, index) => (
                          <div className="dependency-card" key={index}>
                            <h4>Group {index + 1}</h4>

                            <p>{group.length} files involved</p>

                            <ul>
                              {group.map((file) => (
                                <li key={file}>
                                  <code>{file}</code>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p>No circular dependency groups detected in the analyzed graph.</p>
                    )}

                  </div>
                )}
              </section>


              <section className="change-impact-section">
                <h2>Change Impact Analysis</h2>

                <p>
                  Select a Python file to discover which other files
                  may be affected if it changes.
                </p>

                <label htmlFor="changed-file">File to change</label>

                <select
                  id="changed-file"
                  value={impactData?.changed_file || ""}
                  onChange={(event) =>
                    handleLoadChangeImpact(event.target.value)
                  }
                  disabled={impactLoading}
                >
                  <option value="">Select a file</option>

                  {(analysisResult?.python_files || []).map((file) => {
                    const filePath = typeof file === "string" ? file : file.path;

                    return (
                      <option key={filePath} value={filePath}>
                        {filePath}
                      </option>
                    );
                  })}
                </select>

                {impactLoading && <p>Analyzing change impact...</p>}

                {impactError && (
                  <p className="error-message">{impactError}</p>
                )}

                {impactData && (
                  <div className="impact-results">
                    <h3>{impactData.changed_file}</h3>

                    <p>Files analyzed: {impactData.files_analyzed}</p>
                    <p>Total potentially affected: {impactData.total_affected}</p>

                    <h4>Direct Dependents ({impactData.direct_dependents.length})</h4>

                    {impactData.direct_dependents.length > 0 ? (
                      <ul>
                        {impactData.direct_dependents.map((file) => (
                          <li key={file}><code>{file}</code></li>
                        ))}
                      </ul>
                    ) : (
                      <p>No direct dependents found.</p>
                    )}

                    <h4>
                      Indirect Dependents ({impactData.indirect_dependents.length})
                    </h4>

                    {impactData.indirect_dependents.length > 0 ? (
                      <ul>
                        {impactData.indirect_dependents.map((file) => (
                          <li key={file}><code>{file}</code></li>
                        ))}
                      </ul>
                    ) : (
                      <p>No indirect dependents found.</p>
                    )}
                  </div>
                )}
              </section>

            </>
          )}
        </section>

        <p className="footer-note">
          Built for developers navigating unfamiliar codebases.
        </p>
      </main>
    </div>
  );
}

export default App;