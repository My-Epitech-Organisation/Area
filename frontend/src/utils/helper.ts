/*
** EPITECH PROJECT, 2025
** Area
** File description:
** helper
*/

import type { User } from "../types";

export const getStoredUser = (): User | null => {
  const stored = localStorage.getItem("user");
  return stored ? JSON.parse(stored) : null;
};
