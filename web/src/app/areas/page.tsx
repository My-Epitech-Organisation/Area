"use client";
import { useEffect, useMemo, useState } from "react";
import { API_BASE_URL } from "@/lib/api";

type Service = {
  name: string;
  actions: { name: string; description: string }[];
  reactions: { name: string; description: string }[];
};

type Area = {
  id: string;
  service: string;
  action: string;
  reactions: string[];
  name: string;
};

const STORAGE_KEY = 'area.poc.areas';

export default function AreasPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [form, setForm] = useState<Area>({ id: '', name: '', service: '', action: '', reactions: [] });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/about.json`, { cache: 'no-store' });
        const about = await res.json();
        setServices(about?.server?.services || []);
      } catch (e: any) { setError(e.message); }
    })();

    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try { setAreas(JSON.parse(stored)); } catch {}
    }
  }, []);

  function saveAreas(next: Area[]) {
    setAreas(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }

  const selectedService = useMemo(
    () => services.find(s => s.name === form.service),
    [services, form.service]
  );

  function createArea(e: React.FormEvent) {
    e.preventDefault();
    if (!form.service || !form.action || !form.name) return;
    const id = crypto.randomUUID();
    const next = [...areas, { ...form, id }];
    saveAreas(next);
    setForm({ id: '', name: '', service: '', action: '', reactions: [] });
  }

  function removeArea(id: string) {
    saveAreas(areas.filter(a => a.id !== id));
  }

  return (
    <main className="space-y-4">
      <h1 className="text-2xl font-semibold">AREAs</h1>
      {error && <div className="text-red-600">Error: {error}</div>}
      <form onSubmit={createArea} className="rounded-lg border p-4 flex flex-col gap-3" style={{borderColor: 'var(--border)', background: 'var(--card)'}}>
        <div className="grid md:grid-cols-3 gap-3">
          <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
          <select className="border p-2 rounded" value={form.service} onChange={e => setForm(f => ({...f, service: e.target.value, action: '', reactions: []}))} required>
            <option value="">Service</option>
            {services.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
          </select>
          <select className="border p-2 rounded" value={form.action} onChange={e => setForm(f => ({...f, action: e.target.value}))} required disabled={!selectedService}>
            <option value="">Action</option>
            {selectedService?.actions?.map(a => <option key={a.name} value={a.name}>{a.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm font-medium">Reactions</label>
          <div className="flex flex-wrap gap-2 mt-2">
            {selectedService?.reactions?.map(r => {
              const active = form.reactions.includes(r.name);
              return (
                <button key={r.name} type="button" onClick={() => setForm(f => ({...f, reactions: active ? f.reactions.filter(x => x!==r.name) : [...f.reactions, r.name]}))}
                  className={`rounded-md border px-3 py-1.5 text-sm ${active ? 'text-white' : ''}`}
                  style={{borderColor: 'var(--border)', background: active ? 'var(--accent)' : 'transparent'}}>
                  {r.name}
                </button>
              );
            })}
          </div>
        </div>
        <div>
          <button className="inline-flex items-center rounded-md border px-3 py-1.5 text-sm text-white" style={{ background: 'var(--accent)', borderColor: 'transparent' }} type="submit">Add AREA</button>
        </div>
      </form>

      <div className="grid gap-3 md:grid-cols-2">
        {areas.map(a => (
          <div key={a.id} className="rounded-lg border p-4" style={{borderColor: 'var(--border)', background: 'var(--card)'}}>
            <div className="flex items-center justify-between mb-2">
              <a className="text-lg font-semibold underline" href={`/areas/${a.id}`}>{a.name}</a>
              <button className="rounded-md border px-3 py-1.5 text-sm" style={{ borderColor: 'var(--border)' }} onClick={() => removeArea(a.id)}>Delete</button>
            </div>
            <div className="text-sm opacity-80">
              {a.service} • {a.action} → {a.reactions.join(', ') || '—'}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
