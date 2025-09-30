import React, { useState, useMemo } from "react";
import VerticalNav from "../components/VerticalNav";

const quadrantTransforms = [
  "translate(0%, 0%)",
  "translate(-50%, 0%)",
  "translate(-50%, -50%)",
  "translate(0%, -50%)",
];

const Homepage: React.FC = () => {
  const [quad, setQuad] = useState<number>(0);

  const transform = useMemo(() => quadrantTransforms[quad] ?? quadrantTransforms[0], [quad]);

  const nextQuad = () => setQuad((q) => {
    const next = (q + 1) % 4;
    return Math.max(0, Math.min(3, next));
  });

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center overflow-hidden">
      <main className="w-full flex-1 flex items-center justify-center relative">
        <VerticalNav quad={quad} setQuad={setQuad} />
        <div className="w-full h-[100vh] bg-transparent relative overflow-hidden">
          <div
            className="absolute left-0 top-0 w-[200%] h-[200%] grid grid-cols-2 grid-rows-2 transition-transform duration-700 ease-in-out"
            style={{ transform }}
          >
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-indigo-800/40 via-black/30 to-purple-900/40">
              <div className="text-center">
                <h2 className="mb-16 text-9xl text-white font-semibold">AREA</h2>
                <p className="text-5xl text-gray-300 mt-4">"Connect services, trigger actions: automate your routine and let your tools work for you."</p>
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
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-indigo-800/50 via-black/30 to-slate-600/50">
              <div className="text-center">
                <h2 className="mb-16 text-9xl text-white font-semibold">Discover AREA</h2>
                <p className="text-5xl text-gray-300 mt-4">AREA connects your favorite services and creates action→reaction rules to automate daily tasks. Start by exploring the sections below.</p>
                <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
                  <div className="bg-white/5 p-6 rounded-xl backdrop-blur-sm border border-white/10 flex flex-col items-start gap-4">
                    <div className="text-indigo-200 text-4xl">
                      <i className="fa-solid fa-gear"></i>
                    </div>
                    <h3 className="text-2xl text-white font-semibold">Services</h3>
                    <p className="text-lg text-gray-300">Browse available actions and reactions to connect your apps.</p>
                    <a href="/services" className="mt-4 self-stretch inline-block text-center px-4 py-2 bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition">Explore</a>
                  </div>

                  <div className="bg-white/5 p-6 rounded-xl backdrop-blur-sm border border-white/10 flex flex-col items-start gap-4">
                    <div className="text-indigo-200 text-4xl">
                      <i className="fa-solid fa-users"></i>
                    </div>
                    <h3 className="text-2xl text-white font-semibold">About</h3>
                    <p className="text-lg text-gray-300">Meet the team and learn the vision behind AREA project and its goals.</p>
                    <a href="/about" className="mt-4 self-stretch inline-block text-center px-4 py-2 bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition">Learn more</a>
                  </div>

                  <div className="bg-white/5 p-6 rounded-xl backdrop-blur-sm border border-white/10 flex flex-col items-start gap-4">
                    <div className="text-indigo-200 text-4xl">
                      <i className="fa-solid fa-table-columns"></i>
                    </div>
                    <h3 className="text-2xl text-white font-semibold">Dashboard</h3>
                    <p className="text-lg text-gray-300">Access your automations, history, stats and personal settings.</p>
                    <a href="/dashboard" className="mt-4 self-stretch inline-block text-center px-4 py-2 bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition">Open</a>
                  </div>
                </div>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
                  >
                    Next
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-rose-900/40 via-black/30 to-violet-900/40">
              <div className="text-center max-w-6xl">
                <h2 className="text-9xl text-white font-semibold">Get started with AREA</h2>
                <p className="text-5xl text-gray-300 mt-4">Sign up or log in to start creating automations, manage your integrations and access your personal dashboard.</p>
                <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <a href="/login" className="px-10 py-4 text-xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition">Log in</a>
                  <a href="/signup" className="px-10 py-4 text-xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition">Sign up</a>
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
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-slate-600/50 via-black/30 to-emerald-700/40">
              <div className="text-center max-w-4xl">
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
                  <a href="/services" className="px-20 py-6 text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition">See all services</a>
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
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
