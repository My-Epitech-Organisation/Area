import { API_BASE_URL } from "@/lib/api";

export const dynamic = 'force-dynamic';

async function getAbout() {
  const res = await fetch(`${API_BASE_URL}/about.json`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to load about.json: ${res.status}`);
  return res.json();
}

export default async function AboutPage() {
  const data = await getAbout();
  return (
    <main className="space-y-4">
      <h1 className="text-2xl font-semibold">About</h1>
      <div className="rounded-lg border p-4 overflow-auto text-sm" style={{borderColor: 'var(--border)', background: 'var(--card)', color: 'var(--card-foreground)'}}>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </main>
  );
}
