"use client";
import { useEffect, useState } from "react";
import { API_BASE_URL, AppUser } from "@/lib/api";
import { useRouter } from "next/navigation";

type Props = { params: { id: string } };

export default function EditUserPage({ params }: Props) {
  const router = useRouter();
  const id = params.id;
  const [user, setUser] = useState<AppUser | null>(null);
  const [form, setForm] = useState({ name: "", email: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setError(null);
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE_URL}/api/users/${id}/`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data: AppUser = await res.json();
        setUser(data);
        setForm({ name: data.name, email: data.email });
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/users/${id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(`API ${res.status}`);
      router.push('/users');
    } catch (e: any) {
      setError(e.message);
    }
  }

  async function onDelete() {
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/users/${id}/`, { method: 'DELETE' });
      if (!res.ok && res.status !== 204) throw new Error(`API ${res.status}`);
      router.push('/users');
    } catch (e: any) {
      setError(e.message);
    }
  }

  if (loading) return <main className="">Loading…</main>;
  if (error) return <main className="text-red-600">Error: {error}</main>;
  if (!user) return <main className="">Not found</main>;

  return (
    <main className="space-y-4 max-w-xl">
      <h1 className="text-2xl font-semibold">Edit User #{user.id}</h1>
      <form onSubmit={onSave} className="card p-4 flex flex-col gap-2">
        <label className="flex flex-col">
          <span className="text-sm">Name</span>
          <input className="border p-2 rounded" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
        </label>
        <label className="flex flex-col">
          <span className="text-sm">Email</span>
          <input className="border p-2 rounded" type="email" value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))} required />
        </label>
        <div className="flex gap-2 mt-2">
          <button className="btn btn-primary" type="submit">Save</button>
          <button className="btn" type="button" onClick={onDelete}>Delete</button>
        </div>
      </form>
    </main>
  );
}
