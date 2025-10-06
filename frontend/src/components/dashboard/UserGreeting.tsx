/*
** EPITECH PROJECT, 2025
** Area
** File description:
** UserGreeting
*/

import React from "react";
import type { UserGreetingProps } from "../../types";

const UserGreeting: React.FC<UserGreetingProps> = ({ user }) => {
  return (
    <div className="w-full flex items-center justify-center">
      {user ? (
        <p className="text-3xl font-semibold text-indigo-300 mt-2 animate-fade-in">Welcome {user.name}!</p>
      ) : (
        <p className="text-2xl font-semibold text-red-400 mt-2">
          You must be logged in to view this page.
        </p>
      )}
    </div>
  );
};

export default UserGreeting;