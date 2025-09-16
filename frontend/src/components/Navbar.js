import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-3">
          <Link to="/" className="text-xl font-bold">
            AREA Project
          </Link>
          <div className="flex space-x-4">
            <Link to="/" className="hover:text-indigo-200">
              Home
            </Link>
            <Link to="/users" className="hover:text-indigo-200">
              User Management
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
