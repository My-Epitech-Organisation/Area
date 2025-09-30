import React, { useState, useMemo, useRef, useEffect } from "react";
import VerticalNav from "../components/VerticalNav";

const quadrantTransforms = [
  "translate(0%, 0%)",
  "translate(-50%, 0%)",
  "translate(-50%, -50%)",
  "translate(0%, -50%)",
];

const Homepage: React.FC = () => {
  const [quad, setQuad] = useState<number>(0);
  const [overlayVisible, setOverlayVisible] = useState(true);
  const [transitioning, setTransitioning] = useState(false);
  const viewBgMap = ["bg-tl", "bg-tr", "bg-br", "bg-bl"];
  const [baseBgClass, setBaseBgClass] = useState<string>(viewBgMap[0]);
  const transform = useMemo(() => quadrantTransforms[quad] ?? quadrantTransforms[0], [quad]);
  const fadeInRef = useRef<number | null>(null);
  const endRef = useRef<number | null>(null);
  const TOTAL_TRANSITION = 700;
  const START_FADE_IN = Math.round(TOTAL_TRANSITION * 0.7);
  const END_FADE_IN = TOTAL_TRANSITION;

  useEffect(() => {
    return () => {
      if (fadeInRef.current) window.clearTimeout(fadeInRef.current);
      if (endRef.current) window.clearTimeout(endRef.current);
    };
  }, []);

  const animateTo = (target: number) => {
    if (transitioning)
      return;
    setTransitioning(true);
  setBaseBgClass(viewBgMap[Math.max(0, Math.min(3, target))] ?? baseBgClass);
    setQuad(() => Math.max(0, Math.min(3, target)));
    setOverlayVisible(false);
    fadeInRef.current = window.setTimeout(() => {
      setOverlayVisible(true);
    }, START_FADE_IN);

    endRef.current = window.setTimeout(() => {
      setTransitioning(false);
    }, END_FADE_IN);
  };

  const nextQuad = () => animateTo((quad + 1) % 4);

  return (
    <div className={`w-screen min-h-screen ${baseBgClass} flex flex-col items-center overflow-hidden`}>
      <main className="w-full flex-1 flex items-center justify-center relative">
        <VerticalNav quad={quad} setQuad={animateTo} />
        <div className="w-full h-[100vh] bg-transparent relative overflow-hidden">
          <div
            className="absolute left-0 top-0 w-[200%] h-[200%] grid grid-cols-2 grid-rows-2 transition-transform duration-700 ease-in-out"
            style={{ transform }}
          >
            <section className="w-full h-full flex items-center justify-center p-8 relative">
              <div className="absolute inset-0" style={{ transition: 'opacity 210ms ease', opacity: overlayVisible ? 1 : 0 }}>
                <div className="w-full h-full bg-tl" />
              </div>
              <div className="relative z-10 text-center">
                <h2 className="mb-16 text-9xl text-primary font-semibold">AREA</h2>
                <p className="text-5xl text-muted mt-4">"Connect services, trigger actions: automate your routine and let your tools work for you."</p>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
                  >
                    GET STARTED
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 relative">
              <div className="absolute inset-0" style={{ transition: 'opacity 210ms ease', opacity: overlayVisible ? 1 : 0 }}>
                <div className="w-full h-full bg-tr" />
              </div>
              <div className="relative z-10 text-center">
                <h2 className="mb-16 text-9xl text-white font-semibold">Discover AREA</h2>
                <p className="text-5xl text-gray-300 mt-4">AREA connects your favorite services and creates action→reaction rules to automate daily tasks. Start by exploring the sections below.</p>
                <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
                  <div className="bg-white/5 p-6 rounded-xl backdrop-blur-sm border border-white/10 flex flex-col items-start gap-4">
                    <div className="icon-accent text-4xl">
                      <i className="fa-solid fa-gear"></i>
                    </div>
                    <h3 className="text-2xl text-primary font-semibold">Services</h3>
                    <p className="text-lg text-muted">Browse available actions and reactions to connect your apps.</p>
                    <a href="/services" className="mt-4 self-stretch inline-block text-center px-4 py-2 btn-primary rounded-full hover:btn-primary transition">Explore</a>
                  </div>

                  <div className="card-bg p-6 rounded-xl backdrop-blur-sm card-border flex flex-col items-start gap-4">
                    <div className="icon-accent text-4xl">
                      <i className="fa-solid fa-users"></i>
                    </div>
                    <h3 className="text-2xl text-primary font-semibold">About</h3>
                    <p className="text-lg text-muted">Meet the team and learn the vision behind AREA project and its goals.</p>
                    <a href="/about" className="mt-4 self-stretch inline-block text-center px-4 py-2 btn-primary rounded-full hover:btn-primary transition">Learn more</a>
                  </div>

                  <div className="card-bg p-6 rounded-xl backdrop-blur-sm card-border flex flex-col items-start gap-4">
                    <div className="icon-accent text-4xl">
                      <i className="fa-solid fa-table-columns"></i>
                    </div>
                    <h3 className="text-2xl text-primary font-semibold">Dashboard</h3>
                    <p className="text-lg text-muted">Access your automations, history, stats and personal settings.</p>
                    <a href="/dashboard" className="mt-4 self-stretch inline-block text-center px-4 py-2 btn-primary rounded-full hover:btn-primary transition">Open</a>
                  </div>
                </div>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl btn-primary text-black rounded-full hover:btn-primary transition animate-pulse"
                  >
                    Next
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 relative">
              <div className="absolute inset-0" style={{ transition: 'opacity 210ms ease', opacity: overlayVisible ? 1 : 0 }}>
                <div className="w-full h-full bg-bl" />
              </div>
              <div className="relative z-10 text-center max-w-6xl">
                <h2 className="text-9xl text-primary font-semibold">Get started with AREA</h2>
                <p className="text-5xl text-muted mt-4">Sign up or log in to start creating automations, manage your integrations and access your personal dashboard.</p>
                <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <a href="/login" className="px-10 py-4 text-xl btn-primary rounded-full hover:btn-primary transition">Log in</a>
                  <a href="/signup" className="px-10 py-4 text-xl btn-primary rounded-full hover:btn-primary transition">Sign up</a>
                </div>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
                  >
                    BACK
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 relative">
              <div className="absolute inset-0" style={{ transition: 'opacity 210ms ease', opacity: overlayVisible ? 1 : 0 }}>
                <div className="w-full h-full bg-br" />
              </div>
              <div className="relative z-10 text-center max-w-4xl">
                <h2 className="mb-16 -mt-16 text-8xl text-white font-semibold">Examples of what you can automate</h2>
                <p className="text-5xl text-gray-300 my-24">With AREA you can create rules like:</p>
                <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white/5 p-6 rounded-xl border border-white/10 text-left">
                    <h3 className="text-lg text-white font-semibold">Email → Save to Dropbox</h3>
                    <p className="text-lg text-gray-300 mt-2">When you receive an email with attachment, automatically save it to your Dropbox folder.</p>
                  </div>
                  <div className="bg-white/5 p-6 rounded-xl border border-white/10 text-left">
                    <h3 className="text-lg text-white font-semibold">Weather → Notify</h3>
                    <p className="text-lg text-gray-300 mt-2">If tomorrow's forecast predicts rain, send a notification to your phone in the evening.</p>
                  </div>
                  <div className="bg-white/5 p-6 rounded-xl border border-white/10 text-left">
                    <h3 className="text-lg text-white font-semibold">Calendar → Teams</h3>
                    <p className="text-lg text-gray-300 mt-2">When a meeting starts, post a message to your team's Teams channel to remind attendees.</p>
                  </div>
                </div>
                <div className="mt-16 flex justify-center gap-4">
                  <a href="/services" className="px-20 py-6 text-3xl btn-primary rounded-full hover:btn-primary transition">See all services</a>
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl btn-primary rounded-full hover:btn-primary transition animate-pulse"
                  >
                    Next
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Homepage;
