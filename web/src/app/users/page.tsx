"use client";
import { useEffect, useState } from "react";
import { API_BASE_URL, AppUser } from "@/lib/api";

export default function UsersPage() {
  const [users, setUsers] = useState<AppUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", email: "" });

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/users/`, { cache: 'no-store' });
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      setUsers(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(`API ${res.status}`);
      setForm({ name: "", email: "" });
      await load();
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <main className="space-y-4">
      <h1 className="text-2xl font-semibold">Users</h1>
      {error && <div className="text-red-600">Error: {error}</div>}
      <form onSubmit={onCreate} className="card p-4 flex gap-2 items-end">
        <input
          className="border p-2 rounded flex-1"
          placeholder="Name"
          value={form.name}
          onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          required
        />
        <input
          className="border p-2 rounded flex-1"
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
          required
        />
        <button className="btn btn-primary" type="submit">Create</button>
      </form>

      {loading ? (
        <div>Loading…</div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr style={{borderBottom: '1px solid var(--border)'}}>
                <th className="p-2 text-left">ID</th>
                <th className="p-2 text-left">Name</th>
                <th className="p-2 text-left">Email</th>
                <th className="p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} style={{borderTop: '1px solid var(--border)'}}>
                  <td className="p-2">{u.id}</td>
                  <td className="p-2">{u.name}</td>
                  <td className="p-2">{u.email}</td>
                  <td className="p-2 text-center">
                    <a className="underline mr-3" href={`/users/${u.id}`}>Edit</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
