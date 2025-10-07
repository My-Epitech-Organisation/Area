/*
** EPITECH PROJECT, 2025
** Area
** File description:
** ServiceCard
*/

import React from "react";
import type { ServiceCardProps } from "../../types";

const ServiceCard: React.FC<ServiceCardProps> = ({ service }) => {
  if (!service) {
    return (
      <div className="bg-white/10 rounded-xl p-5 backdrop-blur-md border border-white/20">
        <p className="text-gray-400">No service selected</p>
      </div>
    );
  }
  return (
    <div className="bg-white/10 rounded-xl p-5 backdrop-blur-md border border-white/20">
      <h3 className="text-2xl font-semibold mb-3">{service.name}</h3>
      <div className="mb-3">
        <h4 className="text-xl font-semibold text-indigo-300">
            Actions:
        </h4>
            <ul className="list-disc list-inside text-gray-300">
                {service.actions.map((action, i) => (
                <li key={i}>
                <strong>{action.name}</strong>: {action.description}
                </li>
            ))}
            </ul>
        </div>

        <div>
            <h4 className="text-xl font-semibold text-indigo-300">
            Reactions:
            </h4>
            <ul className="list-disc list-inside text-gray-300">
            {service.reactions.map((reaction, j) => (
                <li key={j}>
                <strong>{reaction.name}</strong>: {reaction.description}
                </li>
            ))}
            </ul>
        </div>
    </div>
  );
};

export default ServiceCard;