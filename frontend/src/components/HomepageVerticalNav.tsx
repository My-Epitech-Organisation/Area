import React from 'react';

type Props = {
  quad: number;
  setQuad: (n: number) => void;
};

const HomePageVerticalNav: React.FC<Props> = ({ quad, setQuad }) => {
  const items = ['Home', 'Discover', 'Automations', 'Get Started'];

  return (
    <nav className="fixed left-6 top-1/2 -translate-y-1/2 z-40 flex flex-col gap-3">
      {items.map((label, i) => (
        <button
          key={i}
          onClick={() => setQuad(i)}
          className={`w-36 text-left px-4 py-2 rounded-lg text-sm font-medium transform transition duration-150 ease-out hover:scale-105 hover:translate-x-1 ${
            quad === i
              ? 'bg-indigo-100 text-black'
              : 'bg-white/5 text-white border border-white/10 hover:bg-indigo-300'
          }`}
          aria-pressed={quad === i}
        >
          {label}
        </button>
      ))}
    </nav>
  );
};

export default HomePageVerticalNav;
