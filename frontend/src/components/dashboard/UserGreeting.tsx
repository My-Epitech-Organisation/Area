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
    <div className="user-greeting">
      {user ? (
        <p className="user-greeting-welcome">Welcome {user.name}!</p>
      ) : (
        <p className="user-greeting-error">
          You must be logged in to view this page.
        </p>
      )}
    </div>
  );
};

export default UserGreeting;