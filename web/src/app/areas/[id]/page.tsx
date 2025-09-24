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

export default function AreaDetail({ params }: { params: { id: string } }) {
  const [services, setServices] = useState<Service[]>([]);
  const [area, setArea] = useState<Area | null>(null);
  const [result, setResult] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const res = await fetch(`${API_BASE_URL}/about.json`, { cache: 'no-store' });
      const about = await res.json();
      setServices(about?.server?.services || []);
    })();
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const list: Area[] = JSON.parse(stored);
        setArea(list.find(a => a.id === params.id) || null);
      } catch {}
    }
  }, [params.id]);

  const service = useMemo(() => services.find(s => s.name === area?.service), [services, area]);
  const action = useMemo(() => service?.actions.find(a => a.name === area?.action), [service, area]);
  const reactions = useMemo(() => service?.reactions.filter(r => area?.reactions.includes(r.name)), [service, area]);

  async function simulate() {
    // POC: pas de backend — on simule une exécution
    setResult(`Simulated: action '${action?.name}' would trigger reactions [${(reactions||[]).map(r=>r.name).join(', ')}]`);
  }

  if (!area) return <main className="">Not found</main>;

  return (
    <main className="space-y-4">
      <h1 className="text-2xl font-semibold">{area.name}</h1>
      <div className="rounded-lg border p-4" style={{borderColor: 'var(--border)', background: 'var(--card)'}}>
        <div className="text-sm opacity-80 mb-2">Service</div>
        <div className="font-medium">{area.service}</div>
        <div className="text-sm opacity-80 mt-4 mb-2">Action</div>
        <div className="font-medium">{area.action}{action?.description ? ` — ${action.description}` : ''}</div>
        <div className="text-sm opacity-80 mt-4 mb-2">Reactions</div>
        <ul className="list-disc ml-5">
          {reactions?.map(r => <li key={r.name}><span className="font-medium">{r.name}</span>{r.description ? ` — ${r.description}` : ''}</li>) || <li>—</li>}
        </ul>
        <div className="mt-4">
          <button className="inline-flex items-center rounded-md border px-3 py-1.5 text-sm text-white" style={{ background: 'var(--accent)', borderColor: 'transparent' }} onClick={simulate}>Simulate</button>
        </div>
        {result && <div className="mt-3 text-sm" style={{color: 'var(--foreground)'}}>{result}</div>}
      </div>
    </main>
  );
}
