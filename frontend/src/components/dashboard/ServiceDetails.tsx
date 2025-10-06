/*
** EPITECH PROJECT, 2025
** Area
** File description:
** ServiceDetails
*/

import React from "react";
import type { ServiceCardProps } from "../../types";

const ServiceDetails: React.FC<ServiceCardProps> = ({ service }) => {
    if (!service)
    return (
        <div className="w-3/4 bg-white/5 border border-white/10 rounded-2xl p-6 text-center text-gray-400">
            No service selected
        </div>
    );

    return (
    <div className="w-3/4 bg-white/5 border border-white/10 rounded-2xl p-6 text-white">
      <h3 className="text-center text-3xl mb-4 font-bold text-indigo-400">{service.name}</h3>

      <div className="mb-6">
        <h4 className="text-2xl font-semibold text-indigo-300 mb-2">
            Actions
        </h4>
        <ul className="text-xl list-disc list-inside text-gray-300">
          {service.actions.map((a, i) => (
            <li key={i}>
              <strong>{a.name}</strong> — {a.description}
            </li>
          ))}
        </ul>
      </div>

      <div>
        <h4 className="text-2xl font-semibold text-indigo-300 mb-2">
            Reactions
        </h4>
        <ul className="text-xl list-disc list-inside text-gray-300">
          {service.reactions.map((r, i) => (
            <li key={i}>
              <strong>{r.name}</strong> — {r.description}
            </li>
          ))}
        </ul>
      </div>
    </div>
    );
};

export default ServiceDetails;
