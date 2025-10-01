import React from "react";

const Signup: React.FC = () => {
  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center">
      <header className="w-full pt-28 flex justify-center">
        <h1 className="text-5xl font-bold text-white">Sign Up</h1>
      </header>
      <main className="w-full flex-1 flex items-start justify-center">
        <p className="text-lg text-gray-300 mt-10">Welcome to the Sign Up page!</p>
      </main>
    </div>
  );
};

export default Signup;