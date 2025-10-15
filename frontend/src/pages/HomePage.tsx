/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** Homepage
 */

import React, { useState, useMemo, useRef, useEffect } from 'react';
import HomePageVerticalNav from '../components/HomepageVerticalNav';

const quadrantTransforms = [
  'translate(0%, 0%)',
  'translate(-50%, 0%)',
  'translate(-50%, -50%)',
  'translate(0%, -50%)',
];

const Homepage: React.FC = () => {
  const [quad, setQuad] = useState<number>(0);
  const [overlayVisible, setOverlayVisible] = useState(true);
  const [transitioning, setTransitioning] = useState(false);
  const viewBgMap = ['bg-tl', 'bg-tr', 'bg-br', 'bg-bl'];
  const [baseBgClass, setBaseBgClass] = useState<string>(viewBgMap[0]);
  const transform = useMemo(() => quadrantTransforms[quad] ?? quadrantTransforms[0], [quad]);
  const fadeInRef = useRef<number | null>(null);
  const endRef = useRef<number | null>(null);
  const TOTAL_TRANSITION = 700;
  const END_FADE_IN = TOTAL_TRANSITION;
  const START_FADE_IN = END_FADE_IN;

  useEffect(() => {
    return () => {
      if (fadeInRef.current) window.clearTimeout(fadeInRef.current);
      if (endRef.current) window.clearTimeout(endRef.current);
    };
  }, []);

  const animateTo = (target: number) => {
    if (transitioning) return;
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

  const getOverlayOpacity = (index: number) => {
    return index === quad ? (overlayVisible ? 1 : 0) : 0;
  };

  return (
    <div
      className={`w-screen min-h-screen ${baseBgClass} flex flex-col items-center overflow-hidden`}
    >
      <main className="w-full flex-1 flex items-center justify-center relative">
        <HomePageVerticalNav quad={quad} setQuad={animateTo} />
        <div className="w-full h-[100vh] bg-transparent relative overflow-hidden">
          <div
            className="absolute left-0 top-0 w-[200%] h-[200%] grid grid-cols-2 grid-rows-2 transition-transform duration-700 ease-in-out min-h-[100vh]"
            style={{ transform }}
          >
            <section className="w-full h-full flex items-center justify-center p-4 md:p-8 md:pl-44 lg:pl-48 relative overflow-hidden">
              <div
                className="absolute inset-0"
                style={{ transition: 'opacity 210ms ease', opacity: getOverlayOpacity(0) }}
              >
                <div className="w-full h-full bg-tl" />
              </div>
              <div className="relative z-10 text-center max-w-4xl mx-auto">
                <h2 className="mb-8 md:mb-16 text-2xl md:text-4xl lg:text-6xl xl:text-9xl text-theme-primary font-semibold">
                  AREA
                </h2>
                <p className="text-lg md:text-xl lg:text-3xl xl:text-5xl text-theme-secondary mt-4 px-4">
                  &quot;Connect services, trigger actions: automate your routine and let your tools
                  work for you.&quot;
                </p>
                <div className="mt-6 md:mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-6 md:px-12 lg:px-20 py-3 md:py-5 lg:py-6 text-lg md:text-2xl lg:text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
                  >
                    GET STARTED
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-4 md:p-8 md:pl-44 lg:pl-48 relative overflow-hidden">
              <div
                className="absolute inset-0"
                style={{ transition: 'opacity 210ms ease', opacity: getOverlayOpacity(1) }}
              >
                <div className="w-full h-full bg-tr" />
              </div>
              <div className="relative z-10 text-center w-full max-w-6xl mx-auto px-2">
                <h2 className="mb-2 md:mb-16 text-lg md:text-4xl lg:text-6xl xl:text-9xl text-theme-primary font-semibold leading-tight">
                  Discover AREA
                </h2>
                <p className="text-sm md:text-xl lg:text-3xl xl:text-5xl text-theme-secondary mt-1 md:mt-4 px-1 md:px-2 leading-snug">
                  AREA connects your favorite services and creates action→reaction rules to automate
                  daily tasks.
                  <span className="hidden sm:inline"> Start by exploring the sections below.</span>
                </p>
                <div className="mt-3 md:mt-10 grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-2 md:gap-6 max-w-6xl mx-auto">
                  <div className="card-bg p-2 md:p-6 rounded-lg md:rounded-xl backdrop-blur-sm card-border flex flex-col items-start gap-1 md:gap-4">
                    <div className="icon-accent text-lg md:text-2xl lg:text-4xl">
                      <i className="fa-solid fa-bolt"></i>
                    </div>
                    <h3 className="text-sm md:text-xl lg:text-2xl text-primary font-semibold leading-tight">
                      Areaction
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-muted leading-tight">
                      Create your own automation by connecting actions and reactions.
                    </p>
                    <a
                      href="/Areaction"
                      className="mt-1 md:mt-4 self-stretch inline-block text-center px-2 md:px-4 py-1 md:py-2 btn-primary rounded-full hover:btn-primary transition text-xs md:text-base"
                    >
                      Make it
                    </a>
                  </div>
                  <div className="bg-white/5 p-2 md:p-6 rounded-lg md:rounded-xl backdrop-blur-sm border border-white/10 flex flex-col items-start gap-1 md:gap-4">
                    <div className="icon-accent text-lg md:text-2xl lg:text-4xl">
                      <i className="fa-solid fa-gear"></i>
                    </div>
                    <h3 className="text-sm md:text-xl lg:text-2xl text-primary font-semibold leading-tight">
                      Services
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-muted leading-tight">
                      Browse available actions and reactions to connect your apps.
                    </p>
                    <a
                      href="/services"
                      className="mt-1 md:mt-4 self-stretch inline-block text-center px-2 md:px-4 py-1 md:py-2 btn-primary rounded-full hover:btn-primary transition text-xs md:text-base"
                    >
                      Explore
                    </a>
                  </div>

                  <div className="card-bg p-2 md:p-6 rounded-lg md:rounded-xl backdrop-blur-sm card-border flex flex-col items-start gap-1 md:gap-4">
                    <div className="icon-accent text-lg md:text-2xl lg:text-4xl">
                      <i className="fa-solid fa-users"></i>
                    </div>
                    <h3 className="text-sm md:text-xl lg:text-2xl text-primary font-semibold leading-tight">
                      About
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-muted leading-tight">
                      Meet the team and learn the vision behind AREA project and its goals.
                    </p>
                    <a
                      href="/about"
                      className="mt-1 md:mt-4 self-stretch inline-block text-center px-2 md:px-4 py-1 md:py-2 btn-primary rounded-full hover:btn-primary transition text-xs md:text-base"
                    >
                      Learn more
                    </a>
                  </div>

                  <div className="card-bg p-2 md:p-6 rounded-lg md:rounded-xl backdrop-blur-sm card-border flex flex-col items-start gap-1 md:gap-4">
                    <div className="icon-accent text-lg md:text-2xl lg:text-4xl">
                      <i className="fa-solid fa-table-columns"></i>
                    </div>
                    <h3 className="text-sm md:text-xl lg:text-2xl text-primary font-semibold leading-tight">
                      Dashboard
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-muted leading-tight">
                      Access your automations, history, stats and personal settings.
                    </p>
                    <a
                      href="/dashboard"
                      className="mt-1 md:mt-4 self-stretch inline-block text-center px-2 md:px-4 py-1 md:py-2 btn-primary rounded-full hover:btn-primary transition text-xs md:text-base"
                    >
                      Open
                    </a>
                  </div>
                </div>
                <div className="mt-2 md:mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-4 md:px-12 lg:px-20 py-2 md:py-5 lg:py-6 text-base md:text-2xl lg:text-3xl btn-primary text-black rounded-full hover:btn-primary transition animate-pulse"
                  >
                    Next
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-4 md:p-8 md:pl-44 lg:pl-48 relative overflow-hidden">
              <div
                className="absolute inset-0"
                style={{ transition: 'opacity 210ms ease', opacity: getOverlayOpacity(2) }}
              >
                <div className="w-full h-full bg-bl" />
              </div>
              <div className="relative z-10 text-center max-w-4xl mx-auto px-4">
                <h2 className="text-2xl md:text-4xl lg:text-6xl xl:text-9xl text-theme-primary font-semibold">
                  Get started with AREA
                </h2>
                <p className="text-base md:text-xl lg:text-3xl xl:text-5xl text-theme-secondary mt-2 md:mt-4 px-2">
                  Sign up or log in to start creating automations, manage your integrations and
                  access your personal dashboard.
                </p>
                <div className="mt-4 md:mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 md:gap-4">
                  <a
                    href="/login"
                    className="px-4 md:px-8 lg:px-10 py-2 md:py-4 lg:py-4 text-base md:text-xl lg:text-xl btn-primary rounded-full hover:btn-primary transition"
                  >
                    Log in
                  </a>
                  <a
                    href="/signup"
                    className="px-4 md:px-8 lg:px-10 py-2 md:py-4 lg:py-4 text-base md:text-xl lg:text-xl btn-primary rounded-full hover:btn-primary transition"
                  >
                    Sign up
                  </a>
                </div>
                <div className="mt-4 md:mt-8">
                  <button
                    onClick={nextQuad}
                    className="px-6 md:px-12 lg:px-20 py-3 md:py-5 lg:py-6 text-lg md:text-2xl lg:text-3xl bg-indigo-100 text-black rounded-full hover:bg-indigo-300 transition animate-pulse"
                  >
                    BACK
                  </button>
                </div>
              </div>
            </section>
            <section className="w-full h-full flex items-center justify-center p-4 md:p-8 md:pl-44 lg:pl-48 relative overflow-hidden">
              <div
                className="absolute inset-0"
                style={{ transition: 'opacity 210ms ease', opacity: getOverlayOpacity(3) }}
              >
                <div className="w-full h-full bg-br" />
              </div>
              <div className="relative z-10 text-center max-w-4xl mx-auto px-4">
                <h2 className="mb-6 md:mb-16 -mt-8 md:-mt-16 text-xl md:text-3xl lg:text-5xl xl:text-8xl text-white font-semibold">
                  Examples of what you can automate
                </h2>
                <p className="text-base md:text-xl lg:text-3xl xl:text-5xl text-gray-300 my-8 md:my-24 px-2">
                  With AREA you can create rules like:
                </p>
                <div className="mt-4 md:mt-8 grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-6">
                  <div className="bg-white/5 p-3 md:p-6 rounded-xl border border-white/10 text-left">
                    <h3 className="text-sm md:text-lg text-white font-semibold">
                      Email → Save to Dropbox
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-gray-300 mt-1 md:mt-2">
                      When you receive an email with attachment, automatically save it to your
                      Dropbox folder.
                    </p>
                  </div>
                  <div className="bg-white/5 p-3 md:p-6 rounded-xl border border-white/10 text-left">
                    <h3 className="text-sm md:text-lg text-white font-semibold">
                      Weather → Notify
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-gray-300 mt-1 md:mt-2">
                      If tomorrow&apos;s forecast predicts rain, send a notification to your phone
                      in the evening.
                    </p>
                  </div>
                  <div className="bg-white/5 p-3 md:p-6 rounded-xl border border-white/10 text-left">
                    <h3 className="text-sm md:text-lg text-white font-semibold">
                      Calendar → Teams
                    </h3>
                    <p className="text-xs md:text-sm lg:text-lg text-gray-300 mt-1 md:mt-2">
                      When a meeting starts, post a message to your team&apos;s Teams channel to
                      remind attendees.
                    </p>
                  </div>
                </div>
                <div className="mt-6 md:mt-16 flex flex-col sm:flex-row justify-center gap-3 md:gap-4">
                  <a
                    href="/services"
                    className="px-6 md:px-12 lg:px-20 py-3 md:py-5 lg:py-6 text-lg md:text-2xl lg:text-3xl btn-primary rounded-full hover:btn-primary transition"
                  >
                    See all services
                  </a>
                  <button
                    onClick={nextQuad}
                    className="px-6 md:px-12 lg:px-20 py-3 md:py-5 lg:py-6 text-lg md:text-2xl lg:text-3xl btn-primary rounded-full hover:btn-primary transition animate-pulse"
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
