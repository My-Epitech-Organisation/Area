/*
** EPITECH PROJECT, 2025
** Area
** File description:
** ServiceSelector
*/

import React from "react";
import type { ServiceSelectorProps } from "../../types";

const ServiceSelector: React.FC<ServiceSelectorProps> = ({
  services,
  selectedService,
  onSelect,
}) => {
  return (
    <section className="w-4/5 bg-white/5 border border-white/10 rounded-2xl p-6 shadow-lg mb-10">
      <h2 className="text-3xl mb-6 text-indigo-400 font-semibold text-center">
        Services disponibles
      </h2>
      <div className="w-full overflow-x-auto flex gap-4 pb-4 mb-6 scrollbar-thin scrollbar-thumb-indigo-500 scrollbar-track-transparent">
        {services.map((service, i) => {
          const isActive = selectedService?.name === service.name;
          return (
            <button
              key={i}
              onClick={() => onSelect(service)}
              className={`
                min-w-[200px] px-8 py-6 text-xl rounded-2xl font-semibold text-center
                transition-all duration-300 ease-in-out
                ${isActive
                  ? "bg-indigo-600 text-white shadow-xl scale-105 ring-2 ring-indigo-400"
                  : "bg-white/10 text-gray-300 hover:bg-indigo-400/20 hover:scale-105 hover:shadow-md"
                }
              `}
          >
            {service.name}
            {isActive && (
              <span className="absolute bottom-0 left-0 w-full h-[3px] bg-indigo-400 rounded-t-lg animate-pulse" />
            )}
            </button>
          );
        })}
      {/* </div> */}
      </div>
    </section>
  );
};

export default ServiceSelector;
