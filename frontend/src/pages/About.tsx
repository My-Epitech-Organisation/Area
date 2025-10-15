import React from 'react';

const About: React.FC = () => {
  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center">
      <header className="w-full pt-28 flex justify-center">
        <h1 className="text-4xl md:text-6xl lg:text-8xl font-bold text-theme-primary">About Us</h1>
      </header>
      <main className="w-full flex-1 flex items-start justify-center">
        <p className="text-lg text-theme-secondary mt-10">Welcome to the About Us page!</p>
      </main>
    </div>
  );
};

export default About;
