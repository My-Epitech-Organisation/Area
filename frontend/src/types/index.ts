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
}

export interface User {
  name: string;
}

export interface ServiceSelectorProps {
  services: Service[];
  selectedService: Service | null;
  onSelect: (service: Service) => void;
}

export interface ServiceCardProps {
  service: Service | null;
}

export interface UserGreetingProps {
  user: User | null;
}
