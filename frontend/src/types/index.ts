/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** index
 */

export interface ActionReaction {
  name: string;
  description: string;
}

export interface Service {
  name: string;
  actions: ActionReaction[];
  reactions: ActionReaction[];
  logo?: string | null;
}

export interface User {
  name: string;
  username?: string;
  email?: string;
  id?: number | string;
  email_verified?: boolean;
}

export interface ServiceCardProps {
  service: Service | null;
}
