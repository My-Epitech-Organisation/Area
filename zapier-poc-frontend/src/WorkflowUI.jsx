import React, { useState, useEffect } from "react";

function WorkflowUI() {
  // States for workflow management
  const [workflows, setWorkflows] = useState([]);
  const [name, setName] = useState("");
  const [actions, setActions] = useState("");
  const [result, setResult] = useState("");

  // Fetch workflows on mount
  useEffect(() => {
    fetch("http://localhost:8080/workflows")
      .then((res) => res.json())
      .then(setWorkflows);
  }, []);

  // Create workflow
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!name || !actions) return;
    const wf = { id: Date.now().toString(), name, actions: actions.split(",") };
    const res = await fetch("http://localhost:8080/workflows", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(wf),
    });
    const created = await res.json();
    setWorkflows((prev) => [...prev, created]);
    setName("");
    setActions("");
  };

  // Execute workflow
  const handleExecute = async (wf) => {
    const res = await fetch(`http://localhost:8080/workflows/${wf.id}/execute`, {
      method: "POST",
    });
    const data = await res.json();
    setResult(`Résultat: ${JSON.stringify(data)}`);
  };

  return (
    <div className="bg-white p-6 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Gestion des Workflows</h2>
      <form onSubmit={handleCreate} className="mb-6">
        <input
          className="border p-2 mr-2"
          placeholder="Nom du workflow"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="border p-2 mr-2"
          placeholder="Actions (séparées par des virgules)"
          value={actions}
          onChange={(e) => setActions(e.target.value)}
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">
          Créer
        </button>
      </form>
      <h3 className="text-lg font-semibold mb-2">Liste des workflows</h3>
      <ul className="mb-4">
        {workflows.map((wf, idx) => (
          <li key={idx} className="border p-2 mb-2 rounded flex justify-between items-center">
            <span>
              <span className="font-bold">{wf.name}</span> <span className="text-xs text-gray-500">[{wf.actions.join(", ")}]</span>
            </span>
            <button
              className="bg-green-600 text-white px-3 py-1 rounded"
              onClick={() => handleExecute(wf)}
            >Exécuter</button>
          </li>
        ))}
      </ul>
      {result && <div className="bg-gray-100 p-2 rounded text-sm">{result}</div>}
    </div>
  );
}

export default WorkflowUI;
