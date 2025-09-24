import { API_BASE_URL } from "@/lib/api";

export const dynamic = 'force-dynamic';

type Service = {
  name: string;
  actions: { name: string; description: string }[];
  reactions: { name: string; description: string }[];
};

async function getAbout() {
  const res = await fetch(`${API_BASE_URL}/about.json`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to load about.json: ${res.status}`);
  return res.json();
}

export default async function ServicesPage() {
  const about = await getAbout();
  const services: Service[] = about?.server?.services || [];

  return (
    <main className="space-y-4">
      <h1 className="text-2xl font-semibold">Services</h1>
      {services.length === 0 ? (
        <div className="text-sm opacity-80">No services declared yet.</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {services.map((s: Service) => (
            <div key={s.name} className="rounded-lg border p-4" style={{borderColor: 'var(--border)', background: 'var(--card)'}}>
              <h2 className="text-lg font-semibold mb-2">{s.name}</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium">Actions</h3>
                  <ul className="list-disc ml-5 text-sm">
                    {s.actions?.length ? s.actions.map(a => (
                      <li key={a.name}><span className="font-semibold">{a.name}</span>: {a.description}</li>
                    )) : <li className="opacity-70">—</li>}
                  </ul>
                </div>
                <div>
                  <h3 className="font-medium">Reactions</h3>
                  <ul className="list-disc ml-5 text-sm">
                    {s.reactions?.length ? s.reactions.map(r => (
                      <li key={r.name}><span className="font-semibold">{r.name}</span>: {r.description}</li>
                    )) : <li className="opacity-70">—</li>}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
