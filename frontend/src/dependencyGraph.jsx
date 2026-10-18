
import { useMemo, useEffect, useState } from "react";
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./DependencyGraph.css";

function DependencyGraph({ graphData }) {
    const [searchText, setSearchText] = useState("");
    const [selectedFile, setSelectedFile] = useState("");
    const [flowInstance, setFlowInstance] = useState(null);
    const [searchMessage, setSearchMessage] = useState("");

    const initialNodes = useMemo(
        () =>
            (graphData?.nodes || []).map((node, index) => ({
                id: node.id,
                position: {
                    x: (index % 3) * 250,
                    y: Math.floor(index / 3) * 100,
                },
                data: { label: node.id },
                style: {
                    background: "#1e293b",
                    color: "#ffffff",
                    border: "1px solid #60a5fa",
                    borderRadius: "8px",
                    padding: "10px",
                    width: 220,
                    fontSize: "12px",
                },
            })),
        [graphData?.nodes]
    );

    const initialEdges = useMemo(
        () =>
            (graphData?.edges || []).map((edge, index) => ({
                id: `edge-${index}`,
                source: edge.source,
                target: edge.target,
                animated: false,
                style: { stroke: "#64748b", strokeWidth: 1 },
            })),
        [graphData?.edges]
    );

    const [nodes, setNodes, onNodesChange] =
        useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] =
        useEdgesState(initialEdges);

    // Update the graph when new repository data arrives.
    useEffect(() => {
        setNodes(initialNodes);
        setEdges(initialEdges);
        setSelectedFile("");
        setSearchText("");
        setSearchMessage("");
    }, [initialNodes, initialEdges, setNodes, setEdges]);

    const files = useMemo(
        () => nodes.map((node) => node.id).sort(),
        [nodes]
    );

    const suggestions = useMemo(() => {
        const query = searchText.trim().toLowerCase();

        if (!query) return [];

        return files
            .filter((file) => file.toLowerCase().includes(query))
            .slice(0, 8);
    }, [files, searchText]);

    // Find the selected file and its directly connected neighbors.
    const connectedFiles = useMemo(() => {
        const connected = new Set();

        if (!selectedFile) return connected;

        connected.add(selectedFile);

        edges.forEach((edge) => {
            if (edge.source === selectedFile) {
                connected.add(edge.target);
            }

            if (edge.target === selectedFile) {
                connected.add(edge.source);
            }
        });

        return connected;
    }, [selectedFile, edges]);

    const visibleNodes = useMemo(
        () =>
            nodes.map((node) => {
                const isSelected = node.id === selectedFile;
                const isConnected = connectedFiles.has(node.id);

                return {
                    ...node,
                    style: {
                        ...node.style,
                        opacity: selectedFile
                            ? (isConnected ? 1 : 0.2)
                            : 1,
                        border: isSelected
                            ? "2px solid #facc15"
                            : isConnected && selectedFile
                                ? "2px solid #38bdf8"
                                : "1px solid #60a5fa",
                        background: isSelected
                            ? "#854d0e"
                            : "#1e293b",
                    },
                };
            }),
        [nodes, selectedFile, connectedFiles]
    );

    const visibleEdges = useMemo(
        () =>
            edges.map((edge) => {
                const isConnected =
                    selectedFile &&
                    (edge.source === selectedFile ||
                        edge.target === selectedFile);

                return {
                    ...edge,
                    style: {
                        stroke: isConnected ? "#facc15" : "#64748b",
                        strokeWidth: isConnected ? 2.5 : 1,
                        opacity: selectedFile
                            ? (isConnected ? 1 : 0.12)
                            : 0.7,
                    },
                };
            }),
        [edges, selectedFile]
    );

    function findFile(fileToFind = searchText) {
        const query = fileToFind.trim().toLowerCase();

        if (!query) {
            setSearchMessage("Enter a filename or path to search.");
            return;
        }

        const exactMatch = files.find(
            (file) => file.toLowerCase() === query
        );

        const match =
            exactMatch ||
            files.find((file) =>
                file.toLowerCase().includes(query)
            );

        if (!match) {
            setSelectedFile("");
            setSearchMessage("No matching file found.");
            return;
        }

        setSelectedFile(match);
        setSearchText(match);
        setSearchMessage(`Found: ${match}`);

        const node = nodes.find((item) => item.id === match);

        if (node && flowInstance) {
            flowInstance.setCenter(
                node.position.x + 110,
                node.position.y + 25,
                { zoom: 1.2, duration: 700 }
            );
        }
    }

    function clearSearch() {
        setSearchText("");
        setSelectedFile("");
        setSearchMessage("");
        flowInstance?.fitView({ padding: 0.2, duration: 500 });
    }

    return (
        <div className="dependency-graph">
            <div className="graph-search">
                <input
                    type="text"
                    value={searchText}
                    onChange={(event) => {
                        setSearchText(event.target.value);
                        setSearchMessage("");
                    }}
                    onKeyDown={(event) => {
                        if (event.key === "Enter") findFile();
                        if (event.key === "Escape") clearSearch();
                    }}
                    list="dependency-file-options"
                    placeholder="Search a file, e.g. src/flask/app.py"
                    aria-label="Search repository files"
                />

                <datalist id="dependency-file-options">
                    {suggestions.map((file) => (
                        <option key={file} value={file} />
                    ))}
                </datalist>

                <button onClick={() => findFile()}>
                    Find file
                </button>

                <button
                    className="clear-search"
                    onClick={clearSearch}
                >
                    Clear
                </button>
            </div>

            <p className="graph-search-message" role="status">
                {searchMessage ||
                    (selectedFile
                        ? "Yellow: selected file and its direct connections. Blue: connected files."
                        : "Search for a file to highlight its direct dependencies.")}
            </p>

            <div className="graph-canvas">
                <ReactFlow
                    nodes={visibleNodes}
                    edges={visibleEdges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onInit={setFlowInstance}
                    panOnDrag={true}
                    zoomOnScroll={true}
                    zoomOnPinch={true}
                    fitView
                    minZoom={0.1}
                    maxZoom={2}
                >
                    <Background color="#334155" gap={16} />

                    <Controls
                        showZoom
                        showFitView
                        showInteractive
                    />

                    <MiniMap
                        nodeColor={(node) =>
                            node.id === selectedFile
                                ? "#facc15"
                                : connectedFiles.has(node.id) &&
                                  selectedFile
                                    ? "#38bdf8"
                                    : "#334155"
                        }
                        maskColor="rgba(15, 23, 42, 0.65)"
                    />
                </ReactFlow>
            </div>
        </div>
    );
}

export default DependencyGraph;
