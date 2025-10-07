import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

type AboutService = {
  id: number | string;
  Name: string;
  name?: string;
  description?: string;
  logo?: string | null;
};

const Services: React.FC = () => {
  const imageModules = import.meta.glob("../assets/*.{png,jpg,jpeg,svg,gif}", { eager: true }) as Record<string, { default: string }>; 
  const imagesByName: Record<string, string> = {};
  Object.keys(imageModules).forEach((p) => {
    const parts = p.split("/");
    const file = parts[parts.length - 1];
    const name = file.replace(/\.[^/.]+$/, "").toLowerCase();
    imagesByName[name] = (imageModules as any)[p].default;
  });

  const resolveLogo = (rawLogo: any, nameRaw?: string) => {
    if (rawLogo) {
      const raw = String(rawLogo);
      if (/^(https?:)?\/\//.test(raw) || raw.startsWith("/")) {
        return raw;
      }
      const base = raw.split("/").pop()?.replace(/\.[^/.]+$/, "").toLowerCase() ?? "";
      if (imagesByName[base]) return imagesByName[base];
    }
    const key = (nameRaw ?? "").toString().toLowerCase();
    return imagesByName[key] ?? null;
  };
  const [services, setServices] = useState<AboutService[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fetchAbout = async () => {
      setLoading(true);
      try {
        const res = await fetch("/about.json");
        if (!res.ok)
          throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const list: any[] = data?.server?.services ?? [];
        if (!cancelled) {
          setServices(
            list.map((s) => {
              const id = s.id ?? s.pk ?? s.name;
              const name = (s.Name ?? s.name ?? "").toString();
              const description = s.description ?? s.Description ?? "";

              const rawLogo = s.logo ?? s.icon ?? null;
              let logo: string | null = null;
              if (rawLogo) {
                const raw = String(rawLogo);
                if (/^(https?:)?\/\//.test(raw) || raw.startsWith("/")) {
                  logo = raw;
                } else {
                  const base = raw.split("/").pop()?.replace(/\.[^/.]+$/, "").toLowerCase() ?? "";
                  logo = imagesByName[base] ?? null;
                }
              }
              if (!logo) {
                const key = name.toLowerCase();
                logo = imagesByName[key] ?? null;
              }

              return { id, Name: name, description, logo } as AboutService;
            })
          );
          setError(null);
        }
      } catch (e: any) {
        if (!cancelled)
          setError(e.message ?? "Failed to load services");
      } finally {
        if (!cancelled)
          setLoading(false);
      }
    };

    fetchAbout();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q)
      return services;
    return services.filter((s) => (s.Name || s.name || "").toLowerCase().includes(q));
  }, [services, query]);

  const HISTORY_KEY = "area_service_history";
  const [history, setHistory] = useState<AboutService[]>(() => {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(parsed)) return [];
      return parsed.map((p: any) => ({
        id: p.id,
        Name: p.Name ?? p.name ?? "",
        description: p.description ?? "",
        logo: resolveLogo(p.logo ?? p.icon ?? null, p.Name ?? p.name ?? "")
      }));
    } catch {
      return [];
    }
  });

  const pushHistory = (svc: AboutService) => {
    const normalized: AboutService = {
      id: svc.id,
      Name: svc.Name,
      description: svc.description ?? "",
      logo: resolveLogo(svc.logo ?? null, svc.Name ?? svc.name ?? ""),
    };
    setHistory((prev) => {
      const next = [normalized, ...prev.filter((p) => p.id !== normalized.id)];
      const limited = next.slice(0, 100);
      try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(limited));
      } catch {
      }
      return limited;
    });
  };

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center p-6">
      <header className="w-full pt-20 flex flex-col items-center">
        <h1 className="text-5xl font-bold text-white">Services</h1>
        <p className="text-gray-300 mt-3">Explore available action → reaction services</p>
      </header>

      <main className="w-full max-w-6xl mt-10">
        <div className="flex items-center gap-4 mb-6">
          <input
            aria-label="Search services"
            className="flex-1 px-4 py-3 rounded-lg bg-white/5 placeholder:text-gray-400 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Search services by name..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        {loading ? (
          <p className="text-gray-300">Loading services…</p>
        ) : error ? (
          <p className="text-rose-400">Error loading services: {error}</p>
        ) : filtered.length === 0 ? (
          <div className="py-12 text-center text-gray-300">
            <p className="text-2xl">No services found</p>
            <p className="mt-2 text-sm text-gray-400">Try a different search term or check back later.</p>
          </div>
          ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {filtered.map((s) => (
                <Link
                  to={`/services/${s.id}`}
                  key={s.id}
                  onClick={() => pushHistory(s)}
                  className="group block rounded-xl bg-white/5 p-4 hover:bg-white/6 transition"
                  title={s.description || s.Name}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-20 h-20 rounded-full bg-white/10 flex items-center justify-center overflow-hidden">
                        {s.logo ? (
                          <img src={s.logo} alt={`${s.Name} logo`} className="w-full h-full object-contain" />
                        ) : (
                          <div className="text-2xl font-bold text-white/80">{(s.Name || "?").charAt(0)}</div>
                        )}
                      </div>

                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white group-hover:text-indigo-300">
                        {s.Name}
                      </h3>
                      {s.description && <p className="text-sm text-gray-400 mt-1 line-clamp-2">{s.description}</p>}
                    </div>

                    <div className="text-gray-400">›</div>
                  </div>
                </Link>
              ))}
            </div>

            <section className="mt-10">
              <h2 className="text-2xl font-semibold text-white mb-4">Historique</h2>
              {history.length === 0 ? (
                <div className="py-8 px-6 rounded-lg bg-white/5 text-center text-gray-300">Aucun service visité récemment.</div>
              ) : (
                <div className="flex gap-4 overflow-x-auto pb-2">
                  {history.map((h) => (
                    <Link
                      key={`hist-${h.id}`}
                      to={`/services/${h.id}`}
                      onClick={() => pushHistory(h)}
                      className="min-w-[220px] flex-shrink-0 group rounded-lg bg-white/5 p-3 hover:bg-white/6 transition"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-14 h-14 rounded-full bg-white/10 flex items-center justify-center overflow-hidden">
                          {h.logo ? (
                            <img src={h.logo} alt={`${h.Name} logo`} className="w-full h-full object-contain" />
                          ) : (
                            <div className="text-lg font-semibold text-white/80">{(h.Name || "?").charAt(0)}</div>
                          )}
                        </div>

                        <div>
                          <div className="text-sm font-medium text-white">{h.Name}</div>
                          {h.description && <div className="text-xs text-gray-400 line-clamp-2">{h.description}</div>}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
};

export default Services;
