import React, { useEffect, useMemo, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE, getStoredUser, fetchUserData } from '../utils/helper';
import type { ServiceModel } from '../types/services';
import type { User } from '../types';
import EmailVerificationBanner from '../components/EmailVerificationBanner';

type AboutService = {
  id: number | string;
  Name: string;
  name?: string;
  description?: string;
  logo?: string | null;
};

const Services: React.FC = () => {
  const wheelRef = useRef<HTMLDivElement>(null);
  const carouselContainerRef = useRef<HTMLDivElement | null>(null);
  const historyContainerRef = useRef<HTMLDivElement | null>(null);
  const [wheelRotation, setWheelRotation] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [currentX, setCurrentX] = useState(0);
  const [isAutoRotating, setIsAutoRotating] = useState(false);
  const [flatMode, setFlatMode] = useState(true);
  const flatListRef = useRef<HTMLDivElement | null>(null);
  const [mounted, setMounted] = useState(false);
  const rotationSpeed = 5;
  const radius = window.innerWidth < 768 ? 200 : 350;

  const imageModules = import.meta.glob('../assets/*.{png,jpg,jpeg,svg,gif}', {
    eager: true,
  }) as Record<string, { default: string }>;

  const imagesByName = React.useMemo(() => {
    const result: Record<string, string> = {};
    Object.keys(imageModules).forEach((p) => {
      const parts = p.split('/');
      const file = parts[parts.length - 1];
      const name = file.replace(/\.[^/.]+$/, '').toLowerCase();
      result[name] = imageModules[p].default;
    });
    return result;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const resolveLogo = React.useCallback(
    (rawLogo: string | unknown, nameRaw?: string) => {
      if (rawLogo) {
        const raw = String(rawLogo);
        if (/^(https?:)?\/\//.test(raw) || raw.startsWith('/')) {
          return raw;
        }
        const base =
          raw
            .split('/')
            .pop()
            ?.replace(/\.[^/.]+$/, '')
            .toLowerCase() ?? '';
        if (imagesByName[base]) return imagesByName[base];
      }
      const key = (nameRaw ?? '').toString().toLowerCase();
      return imagesByName[key] ?? null;
    },
    [imagesByName]
  );
  const [services, setServices] = useState<AboutService[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Load user data
    const storedUser = getStoredUser();
    if (storedUser) {
      setUser(storedUser);
    }
  }, []);

  const handleRefreshUserData = async () => {
    try {
      const updatedUser = await fetchUserData();
      if (updatedUser) {
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (err) {
      console.error('Error refreshing user data:', err);
    }
  };

  useEffect(() => {
    const handleFocus = () => {
      handleRefreshUserData();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const fetchAbout = async () => {
      setLoading(true);
      try {
        const baseUrl = API_BASE.replace(/\/api$/, '');
        const res = await fetch(`${baseUrl}/about.json`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const list: ServiceModel[] = data?.server?.services ?? [];
        if (!cancelled) {
          setServices(
            list.map((s) => {
              const id = s.id ?? s.pk ?? s.name;
              const name = (s.Name ?? s.name ?? '').toString();
              const description = s.description ?? s.Description ?? '';

              const rawLogo = s.logo ?? s.icon ?? null;
              let logo: string | null = null;
              if (rawLogo) {
                const raw = String(rawLogo).trim();
                if (/^https?:\/\//i.test(raw)) {
                  logo = raw;
                } else if (raw.startsWith('//')) {
                  logo = `https:${raw}`;
                } else if (raw.startsWith('/')) {
                  logo = `${baseUrl}${raw}`;
                } else {
                  const base =
                    raw
                      .split('/')
                      .pop()
                      ?.replace(/\.[^/.]+$/, '')
                      .toLowerCase() ?? '';
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
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load services');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchAbout();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const id = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(id);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return services;
    return services.filter((s) => (s.Name || s.name || '').toLowerCase().includes(q));
  }, [services, query]);

  const HISTORY_KEY = 'area_service_history';
  const [history, setHistory] = useState<AboutService[]>(() => {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(parsed)) return [];
      return parsed.map((p: Record<string, unknown>) => ({
        id: p.id as string,
        Name: (p.Name as string) ?? (p.name as string) ?? '',
        description: (p.description as string) ?? '',
        logo: resolveLogo(
          (p.logo as string | null) ?? null,
          (p.Name as string | undefined) ?? (p.name as string | undefined) ?? ''
        ),
      }));
    } catch {
      return [];
    }
  });

  const pushHistory = (svc: AboutService) => {
    const normalized: AboutService = {
      id: svc.id,
      Name: svc.Name,
      description: svc.description ?? '',
      logo: resolveLogo(svc.logo ?? null, svc.Name ?? svc.name ?? ''),
    };
    setHistory((prev) => {
      const next = [normalized, ...prev.filter((p) => p.id !== normalized.id)];
      const limited = next.slice(0, 100);
      try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(limited));
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (_) {
        console.error('Could not save service history to localStorage');
      }
      return limited;
    });
  };

  useEffect(() => {
    if (flatMode) {
      return;
    }

    if (!isAutoRotating || isDragging) {
      return;
    }

    let animationFrameId: number;

    const autoRotate = () => {
      setWheelRotation((prev) => {
        const newRotation = prev + 0.04;
        return newRotation;
      });
      animationFrameId = requestAnimationFrame(autoRotate);
    };

    animationFrameId = requestAnimationFrame(autoRotate);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isAutoRotating, isDragging, flatMode]);

  const [hoverCarousel, setHoverCarousel] = useState(false);
  const [hoverHistory, setHoverHistory] = useState(false);

  useEffect(() => {
    if (!flatMode) {
      const timeoutId = setTimeout(() => {
        setIsAutoRotating(true);
      }, 500);
      return () => clearTimeout(timeoutId);
    } else {
      setIsAutoRotating(false);
    }
  }, [flatMode]);

  useEffect(() => {
    if (flatMode)
      return;
    if (!hoverCarousel && !hoverHistory)
      return;

    const handler = (e: WheelEvent) => {
      if (hoverCarousel && !isDragging) {
        if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
          e.preventDefault();
          setWheelRotation((prev) => prev + e.deltaY * 0.2);
        }
      } else if (hoverHistory) {
        if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
          e.preventDefault();
          const el = historyContainerRef.current;
          if (el) el.scrollLeft += e.deltaY;
        }
      }
    };

    document.addEventListener('wheel', handler as EventListener, { passive: false, capture: true });
    return () => document.removeEventListener('wheel', handler as EventListener, true);
  }, [hoverCarousel, hoverHistory, isDragging]);

  useEffect(() => {
    const wheelEl = wheelRef.current;
    const historyEl = historyContainerRef.current;
    const flatEl = flatListRef.current;

    if (!wheelEl && !historyEl && !flatEl)
      return;

    const onWheelCarousel = (e: WheelEvent) => {
      try {
        if (wheelEl && !isDragging) {
          setWheelRotation((prev) => prev + e.deltaY * 0.2);
        }
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (_) {
        console.error('Could not scroll carousel');
      }
    };

    const onWheelHistory = (e: WheelEvent) => {
      try {
        const el = historyEl ?? (e.currentTarget as HTMLDivElement);
        if (!el) return;
        if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
          e.preventDefault();
          el.scrollLeft += e.deltaY;
        }
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (_) {
        console.error('Could not scroll history');
      }
    };

    if (!flatMode) {
      if (wheelEl)
        wheelEl.addEventListener('wheel', onWheelCarousel as EventListener, { passive: false });
      if (historyEl)
        historyEl.addEventListener('wheel', onWheelHistory as EventListener, { passive: false });
    }

    return () => {
      if (!flatMode) {
        if (wheelEl)
          wheelEl.removeEventListener('wheel', onWheelCarousel as EventListener);
        if (historyEl)
          historyEl.removeEventListener('wheel', onWheelHistory as EventListener);
      }
    };
  }, [flatMode, isDragging]);

  const stopAutoRotation = () => {
    setIsAutoRotating(false);
  };

  const [momentum, setMomentum] = useState(0);
  const [lastMoveTime, setLastMoveTime] = useState(0);

  useEffect(() => {
    if (isDragging || !momentum) return;

    let inertiaAnimationId: number;
    const initialMomentum = momentum;
    let currentMomentum = initialMomentum;
    const friction = 0.95;

    const applyInertia = () => {
      if (Math.abs(currentMomentum) < 0.01) {
        setMomentum(0);
        return;
      }

      setWheelRotation((prev) => prev + currentMomentum);
      currentMomentum *= friction;
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
    if (!isDragging) return;

    const now = Date.now();
    const deltaTime = now - lastMoveTime;

    const deltaX = e.clientX - currentX;
    const rotationDelta = deltaX * rotationSpeed * 0.1;

    setWheelRotation((prev) => prev + rotationDelta);
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
    if (!isDragging) return;

    const now = Date.now();
    const deltaTime = now - lastMoveTime;

    const deltaX = e.touches[0].clientX - currentX;
    const rotationDelta = deltaX * rotationSpeed * 0.15;

    setWheelRotation((prev) => prev + rotationDelta);
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
    const angleInRadians = index * angleStep + (wheelRotation * Math.PI) / 180;
    const x = Math.sin(angleInRadians) * radius;
    const z = Math.cos(angleInRadians) * radius;
    const rotationY = (angleInRadians * 180) / Math.PI;
    const normalizedZ = (z + radius) / (radius * 2);
    const isVisible = true;
    const opacity = Math.pow(normalizedZ, 0.4) * 0.5 + 0.5;
    const scale = normalizedZ * 0.35 + 0.65;
    const elevationY = Math.sin(normalizedZ * Math.PI) * 15;

    return { x, z, rotationY, elevationY, isVisible, opacity, scale };
  };

  return (
    <div className="w-screen min-h-screen bg-page-services flex flex-col items-center p-6">
      <header className="w-full pt-20 flex flex-col items-center">
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white">Services</h1>
        <p className="text-gray-300 mt-3">Explore available action → reaction services</p>
      </header>

      {user && <EmailVerificationBanner user={user} onVerificationSent={handleRefreshUserData} />}

      <main className="w-full max-w-6xl mt-12">
        <div className="flex items-center justify-end gap-4 mb-4">
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-300">View mode:</span>
            <div className="flex items-center bg-white/10 rounded-lg p-1 backdrop-blur-sm">
              <button
                onClick={() => setFlatMode(false)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
                  !flatMode
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                  />
                </svg>
                Carousel
              </button>
              <button
                onClick={() => setFlatMode(true)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
                  flatMode
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 10h16M4 14h16M4 18h16"
                  />
                </svg>
                List
              </button>
            </div>
          </div>
        </div>
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
            <p className="mt-2 text-sm text-gray-400">
              Try a different search term or check back later.
            </p>
          </div>
        ) : (
          <>
            <div
              className={`w-full relative group ${flatMode ? 'h-auto' : 'h-[600px] overflow-hidden'}`}
              style={flatMode ? {} : { perspective: '2500px' }}
            >
              {!flatMode && (
                <>
                  <div className="absolute top-1/2 left-4 transform -translate-y-1/2 text-white/30 text-2xl md:text-4xl animate-pulse pointer-events-none z-50">
                    &lt;
                  </div>
                  <div className="absolute top-1/2 right-4 transform -translate-y-1/2 text-white/30 text-2xl md:text-4xl animate-pulse pointer-events-none z-50">
                    &gt;
                  </div>
                </>
              )}
              <div
                ref={carouselContainerRef}
                className={`${flatMode ? 'flex items-center justify-center min-h-[600px] py-8' : 'absolute w-full h-full flex items-center justify-center cursor-grab active:cursor-grabbing'}`}
                onMouseEnter={() => setHoverCarousel(true)}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={() => {
                  setHoverCarousel(false);
                  handleMouseLeave();
                }}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}
              >
                {flatMode ? (
                  <div className="w-full grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-4 px-2 py-4">
                    {filtered.map((s, idx) => (
                      <Link
                        to={`/services/${s.id}`}
                        key={`flat-${s.id}`}
                        onClick={() => pushHistory(s)}
                        className="card-list group rounded-lg p-4 transition transform hover:scale-105 hover:-translate-y-1 duration-200 backdrop-blur-md border border-white/20"
                        style={{
                          animationDelay: `${mounted ? idx * 50 : 0}ms`,
                          background: `linear-gradient(135deg,
                            rgba(139, 92, 246, 0.15) 0%,
                            rgba(59, 130, 246, 0.15) 50%,
                            rgba(16, 185, 129, 0.15) 100%)`,
                          backdropFilter: 'blur(12px)',
                          WebkitBackdropFilter: 'blur(12px)',
                          boxShadow:
                            '0 8px 32px 0 rgba(139, 92, 246, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1) inset',
                        }}
                      >
                        <div
                          className={`flex flex-col items-center gap-3 h-full min-h-[280px] ${mounted ? 'animate-appear' : 'opacity-0'}`}
                        >
                          <div className="w-24 h-24 rounded-lg bg-gradient-to-br from-white/40 to-white/20 flex items-center justify-center overflow-hidden flex-shrink-0 shadow-lg backdrop-blur-sm border border-white/30">
                            {s.logo ? (
                              <img
                                src={s.logo}
                                alt={`${s.Name} logo`}
                                className="w-full h-full object-contain"
                              />
                            ) : (
                              <div className="text-xl md:text-2xl font-bold text-white drop-shadow-lg">
                                {(s.Name || '?').charAt(0)}
                              </div>
                            )}
                          </div>
                          <div className="text-center flex-1 flex flex-col justify-center w-full">
                            <div className="text-base font-bold text-white drop-shadow-md group-hover:text-indigo-200 transition-colors mb-1">
                              {s.Name}
                            </div>
                            {s.description && (
                              <div className="text-xs text-gray-100 line-clamp-2 leading-relaxed px-1 drop-shadow-sm">
                                {s.description}
                              </div>
                            )}
                          </div>
                          <div className="mt-auto px-3 py-1.5 rounded-full bg-gradient-to-r from-indigo-500/80 to-blue-500/80 text-white text-xs font-semibold transform transition-all duration-300 hover:from-indigo-600 hover:to-blue-600 hover:scale-110 shadow-lg backdrop-blur-sm border border-white/20">
                            Explorer
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div
                    ref={wheelRef}
                    className="relative w-[700px] h-[700px]"
                    style={{
                      transformStyle: 'preserve-3d',
                      willChange: 'transform',
                      transform: `rotateX(5deg)`,
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
                      const { x, z, rotationY, opacity, scale } = calculatePosition(
                        index,
                        filtered.length
                      );
                      return (
                        <Link
                          to={`/services/${s.id}`}
                          key={s.id}
                          onClick={() => pushHistory(s)}
                          className={`group absolute top-1/2 left-1/2 w-[200px] h-[220px] -ml-[100px] -mt-[110px] cursor-pointer select-none`}
                          style={{
                            transform: `translateX(${x}px) translateZ(${z}px) translateY(${-calculatePosition(index, filtered.length).elevationY}px) rotateY(${rotationY}deg) scale(${scale})`,
                            transformStyle: 'preserve-3d',
                            transition: isDragging
                              ? 'none'
                              : 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                            opacity: opacity,
                            zIndex: Math.floor(z + 1000),
                          }}
                          title={s.description || s.Name}
                        >
                          <div
                            className="card-carousel relative w-full h-full rounded-xl p-5 flex flex-col items-center justify-center overflow-hidden group-hover:scale-105"
                            style={{
                              transformStyle: 'preserve-3d',
                              transform: `rotateY(${-rotationY}deg)`,
                              transition:
                                'box-shadow 0.5s ease, background 0.5s ease, scale 0.3s ease',
                              background: `linear-gradient(135deg,
                                rgba(139, 92, 246, 0.15) 0%,
                                rgba(59, 130, 246, 0.15) 50%,
                                rgba(16, 185, 129, 0.15) 100%)`,
                              backdropFilter: 'blur(12px)',
                              WebkitBackdropFilter: 'blur(12px)',
                              border: '1px solid rgba(255, 255, 255, 0.18)',
                              boxShadow:
                                z > 0
                                  ? `0 8px 32px 0 rgba(139, 92, 246, 0.25),
                                   0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                                   0 20px 40px -10px rgba(59, 130, 246, 0.3)`
                                  : '0 4px 16px 0 rgba(0, 0, 0, 0.2)',
                            }}
                          >
                            <div className="w-24 h-24 rounded-xl bg-gradient-to-br from-white/40 to-white/20 mb-3 flex items-center justify-center overflow-hidden shadow-lg backdrop-blur-sm border border-white/30">
                              {s.logo ? (
                                <img
                                  src={s.logo}
                                  alt={`${s.Name} logo`}
                                  className="w-full h-full object-contain p-2"
                                  loading="lazy"
                                  decoding="async"
                                />
                              ) : (
                                <div className="text-2xl md:text-3xl font-bold text-white drop-shadow-lg">
                                  {(s.Name || '?').charAt(0)}
                                </div>
                              )}
                            </div>
                            <h3 className="text-lg font-semibold text-white text-center line-clamp-1 drop-shadow-md">
                              {s.Name}
                            </h3>
                            {s.description && (
                              <p className="text-xs text-gray-100 mt-2 text-center line-clamp-2 overflow-hidden drop-shadow-sm">
                                {s.description}
                              </p>
                            )}
                            <div className="mt-3 px-4 py-1.5 rounded-full bg-gradient-to-r from-indigo-500/80 to-blue-500/80 text-white text-xs font-medium transform transition-all duration-300 hover:from-indigo-600 hover:to-blue-600 hover:scale-110 shadow-lg backdrop-blur-sm border border-white/20">
                              Explorer
                            </div>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <section className="mt-8">
              <h2 className="text-lg md:text-xl font-semibold text-white mb-3">History</h2>
              {history.length === 0 ? (
                <div className="py-8 px-6 rounded-lg bg-white/5 text-center text-gray-300">
                  No services visited recently.
                </div>
              ) : (
                <div
                  ref={historyContainerRef}
                  onMouseEnter={() => setHoverHistory(true)}
                  onMouseLeave={() => setHoverHistory(false)}
                  className="flex gap-4 overflow-x-auto pb-4 px-1 scrollbar-thin scrollbar-thumb-indigo-500/50 scrollbar-track-transparent scrollbar-visible snap-x snap-mandatory"
                  style={{ overscrollBehavior: 'none' }}
                >
                  {history.map((h, idx) => (
                    <Link
                      key={`hist-${h.id}`}
                      to={`/services/${h.id}`}
                      onClick={() => pushHistory(h)}
                      className="card-history snap-start min-w-[240px] h-[260px] flex-shrink-0 group rounded-lg p-4 transition-all duration-300 backdrop-blur-md border border-white/20"
                      style={{
                        background: `linear-gradient(135deg,
                          rgba(139, 92, 246, 0.15) 0%,
                          rgba(59, 130, 246, 0.15) 50%,
                          rgba(16, 185, 129, 0.15) 100%)`,
                        backdropFilter: 'blur(12px)',
                        WebkitBackdropFilter: 'blur(12px)',
                        boxShadow:
                          '0 8px 32px 0 rgba(139, 92, 246, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1) inset',
                      }}
                    >
                      <div
                        className={`${mounted ? 'animate-appear' : 'opacity-0'} flex flex-col items-center gap-3 h-full`}
                        style={{ animationDelay: `${mounted ? idx * 70 : 0}ms` }}
                      >
                        <div className="w-28 h-28 rounded-xl bg-white/36 flex items-center justify-center overflow-hidden shadow-2xl">
                          {h.logo ? (
                            <img
                              src={h.logo}
                              alt={`${h.Name} logo`}
                              className="w-full h-full object-contain"
                              loading="lazy"
                              decoding="async"
                            />
                          ) : (
                            <div className="text-xl md:text-2xl font-semibold text-white/80">
                              {(h.Name || '?').charAt(0)}
                            </div>
                          )}
                        </div>

                        <div className="text-center mt-2">
                          <div className="text-sm font-medium text-white group-hover:text-indigo-200 transition-colors">
                            {h.Name}
                          </div>
                          {h.description && (
                            <div className="text-xs text-gray-400 line-clamp-3 mt-2">
                              {h.description}
                            </div>
                          )}
                        </div>
                        <div className="mt-auto text-xs text-gray-400">Recently visited</div>
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
