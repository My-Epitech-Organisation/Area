/*
** EPITECH PROJECT, 2025
** Area
** File description:
** helper
*/

import type { User } from "../types";

export const getStoredUser = (): User | null => {
  const stored = localStorage.getItem("user");
  if (!stored)
    return null;
  try {
    return JSON.parse(stored) as User;
  } catch (e) {
    return null;
  }
};
