// Frontend React pour le POC SQL vs NoSQL
// Ce composant permet d'ajouter et de lister des utilisateurs en SQL et NoSQL
// Les commentaires expliquent chaque étape pour débutant/intermédiaire

import React, { useState, useEffect } from "react";
import WorkflowUI from "./WorkflowUI";

function App() {
  // States pour le formulaire et les listes
  const [name, setName] = useState(""); // Nom de l'utilisateur à créer
  const [usersSQL, setUsersSQL] = useState([]); // Utilisateurs SQL
  const [usersNoSQL, setUsersNoSQL] = useState([]); // Utilisateurs NoSQL
  const [storageType, setStorageType] = useState("sql"); // Type de stockage choisi

    // Edition utilisateur
  const [editId, setEditId] = useState(null);
  const [editName, setEditName] = useState("");

  // Modifier un utilisateur
  const handleEdit = (user, type) => {
    setEditId(user.id);
    setEditName(user.name);
    setStorageType(type);
  };

  // Valider la modification
  const handleUpdate = async (type) => {
    const url = type === "sql"
      ? `http://localhost:8080/users/sql/${editId}`
      : `http://localhost:8080/users/nosql/${editId}`;
    await fetch(url, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: editName }),
    });
    if (type === "sql") {
      setUsersSQL((prev) => prev.map(u => u.id === editId ? { ...u, name: editName } : u));
    } else {
      setUsersNoSQL((prev) => prev.map(u => u.id === editId ? { ...u, name: editName } : u));
    }
    setEditId(null);
    setEditName("");
  };

  // Supprimer un utilisateur
  const handleDelete = async (id, type) => {
    const url = type === "sql"
      ? `http://localhost:8080/users/sql/${id}`
      : `http://localhost:8080/users/nosql/${id}`;
    await fetch(url, { method: "DELETE" });
    if (type === "sql") {
      setUsersSQL((prev) => prev.filter(u => u.id !== id));
    } else {
      setUsersNoSQL((prev) => prev.filter(u => u.id !== id));
    }
  };

  // Récupère les utilisateurs au chargement
  useEffect(() => {
    fetch("http://localhost:8080/users/sql")
      .then((res) => res.json())
      .then((data) => setUsersSQL(Array.isArray(data) ? data : []));
    fetch("http://localhost:8080/users/nosql")
      .then((res) => res.json())
      .then((data) => {
        // Convertit l'id MongoDB en string
        if (Array.isArray(data)) {
          setUsersNoSQL(
            data.map(u => {
              let mongoId = u.id;
              if (mongoId && typeof mongoId === "object" && mongoId.$oid) mongoId = mongoId.$oid;
              else if (typeof mongoId === "string") mongoId = mongoId;
              else mongoId = Date.now().toString();
              return { id: mongoId, name: u.name };
            })
          );
        } else {
          setUsersNoSQL([]);
        }
      });
  }, []);

  // Fonction pour ajouter un utilisateur
  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    // Choix du backend selon le type
    const url =
      storageType === "sql"
        ? "http://localhost:8080/users/sql"
        : "http://localhost:8080/users/nosql";
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const data = await res.json();
    if (storageType === "sql") {
      setUsersSQL((prev) => [...prev, { id: data.id || Date.now().toString(), name: data.name }]);
    } else {
      // Mongo renvoie l'id sous forme d'objet { "$oid": ... }
      let mongoId = data.id;
      if (mongoId && typeof mongoId === "object" && mongoId.$oid) mongoId = mongoId.$oid;
      else if (typeof mongoId === "string") mongoId = mongoId;
      else mongoId = Date.now().toString();
      setUsersNoSQL((prev) => [...prev, { id: mongoId, name: data.name }]);
    }
    setName("");
  };

  // Tab state: 'workflow' or 'crud'
  const [activeTab, setActiveTab] = useState('workflow');

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6 text-center">POC Zapier & SQL/NoSQL Comparison</h1>
      <div className="flex justify-center mb-8">
        <button
          className={`px-4 py-2 rounded-l border ${activeTab === 'workflow' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
          onClick={() => setActiveTab('workflow')}
        >Workflow</button>
        <button
          className={`px-4 py-2 rounded-r border ${activeTab === 'crud' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
          onClick={() => setActiveTab('crud')}
        >SQL/NoSQL Comparison</button>
      </div>
      {activeTab === 'crud' ? (
        <WorkflowUI />
      ) : (
        <div>
          {/* Formulaire d'ajout d'utilisateur */}
          <form onSubmit={handleAdd} className="mb-6">
            <input
              className="border p-2 mr-2"
              placeholder="Nom de l'utilisateur"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <select
              className="border p-2 mr-2"
              value={storageType}
              onChange={(e) => setStorageType(e.target.value)}
            >
              <option value="sql">SQL (SQLite)</option>
              <option value="nosql">NoSQL (MongoDB)</option>
            </select>
            <button className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">
              Ajouter
            </button>
          </form>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Utilisateurs SQL</h2>
              <ul>
                {usersSQL.map((u) => (
                  <li key={u.id} className="border p-2 mb-2 rounded flex items-center justify-between">
                    {editId === u.id ? (
                      <>
                        <input
                          className="border p-1 mr-1"
                          value={editName}
                          onChange={e => setEditName(e.target.value)}
                        />
                        <button className="bg-green-600 text-white px-2 py-1 rounded mr-2" onClick={() => handleUpdate("sql")}>Valider</button>
                        <button className="bg-gray-400 text-white px-2 py-1 rounded" onClick={() => {setEditId(null); setEditName("");}}>Annuler</button>
                      </>
                    ) : (
                      <>
                        {u.name} <span className="text-xs text-gray-500">(id: {u.id})</span>
                        <button className="bg-yellow-500 text-white px-2 py-1 rounded ml-2" onClick={() => handleEdit(u, "sql")}>Modifier</button>
                        <button className="bg-red-600 text-white px-2 py-1 rounded ml-2" onClick={() => handleDelete(u.id, "sql")}>Supprimer</button>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-2">Utilisateurs NoSQL</h2>
              <ul>
                {usersNoSQL.map((u) => (
                  <li key={u.id} className="border p-2 mb-2 rounded flex items-center justify-between">
                    {editId === u.id ? (
                      <>
                        <input
                          className="border p-1 mr-2"
                          value={editName}
                          onChange={e => setEditName(e.target.value)}
                        />
                        <button className="bg-green-600 text-white px-2 py-1 rounded mr-2" onClick={() => handleUpdate("nosql")}>Valider</button>
                        <button className="bg-gray-400 text-white px-2 py-1 rounded" onClick={() => {setEditId(null); setEditName("");}}>Annuler</button>
                      </>
                    ) : (
                      <>
                        {u.name} <span className="text-xs text-gray-500">(id: {u.id})</span>
                        <button className="bg-yellow-500 text-white px-2 py-1 rounded ml-2" onClick={() => handleEdit(u, "nosql")}>Modifier</button>
                        <button className="bg-red-600 text-white px-2 py-1 rounded ml-2" onClick={() => handleDelete(u.id, "nosql")}>Supprimer</button>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
