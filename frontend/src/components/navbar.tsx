import React from "react";
import { Link } from "react-router-dom";

const Navbar: React.FC = () => {
  return (
    <nav className="w-full fixed top-0 left-0 z-50 bg-black/50 backdrop-blur-sm border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-16 flex items-center justify-between">
          <div className="flex items-center">
            <Link to="/homepage" className="text-white text-lg font-semibold hover:text-indigo-300 transition">
              Area
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
