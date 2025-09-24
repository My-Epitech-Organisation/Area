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
    <main className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">About</h1>
      <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
        {JSON.stringify(data, null, 2)}
      </pre>
    </main>
  );
}
