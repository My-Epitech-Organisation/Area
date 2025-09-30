import React, { useState, useMemo } from "react";

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
        <div className="w-full h-[100vh] bg-transparent relative overflow-hidden">
          <div
            className="absolute left-0 top-0 w-[200%] h-[200%] grid grid-cols-2 grid-rows-2 transition-transform duration-700 ease-in-out"
            style={{ transform }}
          >
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-indigo-800/40 via-black/30 to-purple-900/40">
              <div className="text-center">
                <h2 className="mb-16 text-9xl text-white font-semibold">AREA</h2>
                <p className="text-5xl text-gray-300 mt-4">Service automation</p>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-20 py-6 text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
                  >
                    GET START
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-indigo-800/50 via-black/30 to-slate-600/50">
              <div className="text-center">
                <h2 className="text-5xl text-white font-semibold">Top Right</h2>
                <p className="text-xl text-gray-300 mt-4">Secondary features or navigation.</p>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-8 py-3 text-lg bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition"
                  >
                    NEXT
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-rose-900/40 via-black/30 to-violet-900/40">
              <div className="text-center">
                <h2 className="text-5xl text-white font-semibold">Bottom Left</h2>
                <p className="text-xl text-gray-300 mt-4">Contact or final CTA.</p>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-8 py-3 text-lg bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition"
                  >
                    BACK
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-8 bg-gradient-to-br from-slate-600/50 via-black/30 to-emerald-700/40">
              <div className="text-center">
                <h2 className="text-5xl text-white font-semibold">Bottom Right</h2>
                <p className="text-xl text-gray-300 mt-4">Details, demos or forms.</p>
                <div className="mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-8 py-3 text-lg bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition"
                  >
                    NEXT
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
