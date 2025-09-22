/*
** EPITECH PROJECT, 2025
** Area
** File description:
** App
*/

import { useEffect, useState } from "react";

interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

function App() {
  const [users, setUsers] = useState<User[]>([]);
  const [newUser, setNewUser] = useState({ name: "", email: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_BASE = "http://localhost:8080";

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_BASE}/users`);
      if (!response.ok) throw new Error("Failed to fetch users");
      const data = await response.json();
      setUsers(data);
      setError("");
    } catch (err) {
      setError("Failed to load users");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUser.name || !newUser.email) return;

    try {
      const response = await fetch(`${API_BASE}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to add user");
      }

      setNewUser({ name: "", email: "" });
      fetchUsers(); // Refresh the list
    } catch (err: any) {
      setError(err.message);
    }
  };

  const deleteUser = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE}/users/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete user");

      fetchUsers(); // Refresh the list
    } catch (err) {
      setError("Failed to delete user");
      console.error(err);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>AREA User Management</h1>

      {error && (
        <div style={{
          color: "red",
          backgroundColor: "#ffe6e6",
          padding: "10px",
          borderRadius: "4px",
          marginBottom: "20px"
        }}>
          {error}
        </div>
      )}

      {/* Add User Form */}
      <div style={{
        backgroundColor: "#f5f5f5",
        padding: "20px",
        borderRadius: "8px",
        marginBottom: "20px"
      }}>
        <h2>Add New User</h2>
        <form onSubmit={addUser}>
          <div style={{ marginBottom: "10px" }}>
            <input
              type="text"
              placeholder="Name"
              value={newUser.name}
              onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
              style={{
                padding: "8px",
                marginRight: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                width: "200px"
              }}
            />
            <input
              type="email"
              placeholder="Email"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              style={{
                padding: "8px",
                marginRight: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                width: "200px"
              }}
            />
            <button
              type="submit"
              style={{
                padding: "8px 16px",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer"
              }}
            >
              Add User
            </button>
          </div>
        </form>
      </div>

      {/* Users List */}
      <div>
        <h2>Users List</h2>
        {loading ? (
          <p>Loading users...</p>
        ) : users.length === 0 ? (
          <p>No users found. Add your first user above!</p>
        ) : (
          <div style={{ display: "grid", gap: "10px" }}>
            {users.map((user) => (
              <div
                key={user.id}
                style={{
                  border: "1px solid #ddd",
                  padding: "15px",
                  borderRadius: "8px",
                  backgroundColor: "white",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}
              >
                <div>
                  <h3 style={{ margin: "0 0 5px 0" }}>{user.name}</h3>
                  <p style={{ margin: "0", color: "#666" }}>{user.email}</p>
                  <small style={{ color: "#999" }}>
                    Created: {new Date(user.created_at).toLocaleDateString()}
                  </small>
                </div>
                <button
                  onClick={() => deleteUser(user.id)}
                  style={{
                    padding: "6px 12px",
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer"
                  }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ marginTop: "40px", padding: "20px", backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
        <a href="/apks/client.apk" download style={{ color: "#007bff", textDecoration: "none" }}>
          📱 Download Mobile APK
        </a>
      </div>
    </div>
  );
}

export default App;
