import React, { useEffect, useMemo, useState, useRef } from "react";
import { Link } from "react-router-dom";

type AboutService = {
  id: number | string;
  Name: string;
  name?: string;
  description?: string;
  logo?: string | null;
};

const Services: React.FC = () => {
  const wheelRef = useRef<HTMLDivElement>(null);
  const [wheelRotation, setWheelRotation] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [currentX, setCurrentX] = useState(0);
  const [isAutoRotating, setIsAutoRotating] = useState(false);
  const rotationSpeed = 5;
  const radius = 350;

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
      if (!Array.isArray(parsed))
        return [];
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

  useEffect(() => {
    let animationFrameId: number;
    let lastTime = 0;

    const autoRotate = (currentTime: number) => {
      if (!lastTime) lastTime = currentTime;

      if (isAutoRotating && !isDragging) {
        setWheelRotation(prev => prev + 0.03);
      }

      lastTime = currentTime;
      animationFrameId = requestAnimationFrame(autoRotate);
    };

    const timeoutId = setTimeout(() => {
      setIsAutoRotating(true);
      animationFrameId = requestAnimationFrame(autoRotate);
    }, 2000);

    return () => {
      cancelAnimationFrame(animationFrameId);
      clearTimeout(timeoutId);
    };
  }, [isDragging, isAutoRotating]);

  const stopAutoRotation = () => {
    setIsAutoRotating(false);
  };

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    stopAutoRotation();
    const newRotation = wheelRotation + (e.deltaY * 0.2);
    setWheelRotation(newRotation);
    e.preventDefault();
  };

  const [momentum, setMomentum] = useState(0);
  const [lastMoveTime, setLastMoveTime] = useState(0);

  useEffect(() => {
    if (isDragging || !momentum)
      return;

    let inertiaAnimationId: number;
    let friction = 0.95;

    const applyInertia = () => {
      if (Math.abs(momentum) < 0.01) {
        setMomentum(0);
        return;
      }

      setWheelRotation(prev => prev + momentum);
      setMomentum(momentum * friction);
      inertiaAnimationId = requestAnimationFrame(applyInertia);
    };

    inertiaAnimationId = requestAnimationFrame(applyInertia);

    return () => {
      cancelAnimationFrame(inertiaAnimationId);
    };
  }, [isDragging, momentum]);

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    stopAutoRotation();
    setIsDragging(true);
    setCurrentX(e.clientX);
    setMomentum(0);
    setLastMoveTime(Date.now());
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging)
      return;

    const now = Date.now();
    const deltaTime = now - lastMoveTime;

    const deltaX = e.clientX - currentX;
    const rotationDelta = deltaX * rotationSpeed * 0.1;

    setWheelRotation(prev => prev + rotationDelta);
    setCurrentX(e.clientX);
    setLastMoveTime(now);

    if (deltaTime > 0) {
      const velocity = deltaX / deltaTime;
      setMomentum(velocity * rotationSpeed * 0.1);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    const inertiaTimeout = setTimeout(() => setIsAutoRotating(true), 3000);
    return () => clearTimeout(inertiaTimeout);
  };

  const handleMouseLeave = () => {
    if (isDragging) {
      setIsDragging(false);
      setTimeout(() => setIsAutoRotating(true), 3000);
    }
  };

  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    stopAutoRotation();
    setIsDragging(true);
    setCurrentX(e.touches[0].clientX);
    setMomentum(0);
    setLastMoveTime(Date.now());
    e.preventDefault();
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (!isDragging)
      return;

    const now = Date.now();
    const deltaTime = now - lastMoveTime;

    const deltaX = e.touches[0].clientX - currentX;
    const rotationDelta = deltaX * rotationSpeed * 0.15;

    setWheelRotation(prev => prev + rotationDelta);
    setCurrentX(e.touches[0].clientX);
    setLastMoveTime(now);

    if (deltaTime > 0) {
      const velocity = deltaX / deltaTime;
      setMomentum(velocity * rotationSpeed * 0.15);
    }

    e.preventDefault();
  };

  const handleTouchEnd = () => {
    setIsDragging(false);

    setTimeout(() => setIsAutoRotating(true), 4000);
  };

  const calculatePosition = (index: number, total: number) => {
    const angleStep = (2 * Math.PI) / total;

    const angleInRadians = (index * angleStep) + (wheelRotation * Math.PI / 180);

    const x = Math.sin(angleInRadians) * radius;
    const z = Math.cos(angleInRadians) * radius;

    const rotationY = (angleInRadians * 180 / Math.PI);

    const normalizedZ = (z + radius) / (radius * 2);

    const isVisible = z > -radius * 0.7;

    const opacity = isVisible ? Math.pow(normalizedZ, 0.8) * 0.7 + 0.3 : 0;

    const scale = isVisible ? normalizedZ * 0.4 + 0.6 : 0.6;

    const elevationY = isVisible ? Math.sin(normalizedZ * Math.PI) * 20 : 0;

    return { x, z, rotationY, elevationY, isVisible, opacity, scale };
  };

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center p-6">
      <header className="w-full pt-20 flex flex-col items-center">
        <h1 className="text-5xl font-bold text-white">Services</h1>
        <p className="text-gray-300 mt-3">Explore available action → reaction services</p>
      </header>

      <main className="w-full max-w-7xl mt-10">
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
            <div className="w-full h-[600px] relative overflow-hidden my-10 group"
                 style={{ perspective: '1800px' }}>
              <div className="absolute top-1/2 left-4 transform -translate-y-1/2 text-white/30 text-4xl animate-pulse pointer-events-none z-50">
                &lt;
              </div>
              <div className="absolute top-1/2 right-4 transform -translate-y-1/2 text-white/30 text-4xl animate-pulse pointer-events-none z-50">
                &gt;
              </div>
              <div
                className="absolute w-full h-full flex items-center justify-center cursor-grab active:cursor-grabbing"
                onWheel={handleWheel}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseLeave}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}
              >
                <div
                  ref={wheelRef}
                  className="relative w-[700px] h-[700px]"
                  style={{
                    transformStyle: 'preserve-3d',
                    willChange: 'transform',
                    transform: `rotateX(10deg)`,
                    transition: isDragging ? 'none' : 'transform 0.5s ease-out',
                  }}
                >
                  <div
                    className="absolute w-[800px] h-[800px] rounded-full -bottom-[150px] left-1/2 transform -translate-x-1/2 bg-gradient-radial from-indigo-900/20 to-transparent" 
                    style={{
                      transform: 'rotateX(90deg) translateZ(-200px)',
                      filter: 'blur(5px)',
                      opacity: 0.7,
                    }}
                  />
                  {filtered.map((s, index) => {
                    const { x, z, rotationY, isVisible, opacity, scale } = calculatePosition(index, filtered.length);
                    return (
                      <Link
                        to={`/services/${s.id}`}
                        key={s.id}
                        onClick={() => pushHistory(s)}
                        className={`absolute top-1/2 left-1/2 w-[200px] h-[220px] -ml-[100px] -mt-[110px] cursor-pointer select-none ${!isVisible ? 'pointer-events-none' : ''}`}
                        style={{
                          transform: `translateX(${x}px) translateZ(${z}px) translateY(${-calculatePosition(index, filtered.length).elevationY}px) rotateY(${rotationY}deg) scale(${scale})`,
                          transformStyle: 'preserve-3d',
                          transition: isDragging ? 'none' : 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                          opacity: opacity,
                          zIndex: Math.floor(z + 1000),
                        }}
                        title={s.description || s.Name}
                      >
                        <div
                          className="w-full h-full rounded-xl bg-gradient-to-br from-white/15 to-white/5 backdrop-blur-sm p-5 flex flex-col items-center justify-center shadow-xl border border-white/10 overflow-hidden group hover:from-indigo-500/20 hover:to-white/10 transition-colors duration-300"
                          style={{
                            transformStyle: 'preserve-3d',
                            transform: `rotateY(${-rotationY}deg)`,
                            boxShadow: z > 0
                              ? '0 10px 30px -5px rgba(0, 0, 0, 0.3), 0 0 15px -3px rgba(255, 255, 255, 0.1), inset 0 0 10px rgba(255, 255, 255, 0.1)'
                              : 'none',
                          }}
                        >
                          <div className="w-24 h-24 rounded-xl bg-white/10 mb-3 flex items-center justify-center overflow-hidden">
                            {s.logo ? (
                              <img
                                src={s.logo}
                                alt={`${s.Name} logo`}
                                className="w-full h-full object-contain p-2"
                                loading="lazy"
                                decoding="async"
                              />
                            ) : (
                              <div className="text-3xl font-bold text-white/80">{(s.Name || "?").charAt(0)}</div>
                            )}
                          </div>
                          <h3 className="text-lg font-semibold text-white text-center line-clamp-1">
                            {s.Name}
                          </h3>
                          {s.description &&
                            <p className="text-xs text-gray-300 mt-2 text-center line-clamp-2 overflow-hidden">
                              {s.description}
                            </p>
                          }
                          <div className="mt-3 px-4 py-1.5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-medium transform transition-all duration-300 group-hover:bg-indigo-600/40 group-hover:text-indigo-100 group-hover:scale-110">
                            Explorer
                          </div>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            </div>

            <section className="mt-16">
              <h2 className="text-2xl font-semibold text-white mb-4">Historique</h2>
              {history.length === 0 ? (
                <div className="py-8 px-6 rounded-lg bg-white/5 text-center text-gray-300">Aucun service visité récemment.</div>
              ) : (
                <div className="flex gap-4 overflow-x-auto pb-4 px-1 scrollbar-thin scrollbar-thumb-indigo-500/50 scrollbar-track-transparent snap-x snap-mandatory">
                  {history.map((h) => (
                    <Link
                      key={`hist-${h.id}`}
                      to={`/services/${h.id}`}
                      onClick={() => pushHistory(h)}
                      className="snap-start min-w-[220px] flex-shrink-0 group rounded-lg bg-white/5 p-4 hover:bg-white/10 transition transform hover:scale-105 hover:-translate-y-1 duration-200"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-16 h-16 rounded-xl bg-white/10 flex items-center justify-center overflow-hidden">
                          {h.logo ? (
                            <img
                              src={h.logo}
                              alt={`${h.Name} logo`}
                              className="w-full h-full object-contain"
                              loading="lazy"
                              decoding="async"
                            />
                          ) : (
                            <div className="text-lg font-semibold text-white/80">{(h.Name || "?").charAt(0)}</div>
                          )}
                        </div>

                        <div>
                          <div className="text-sm font-medium text-white group-hover:text-indigo-200 transition-colors">{h.Name}</div>
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
