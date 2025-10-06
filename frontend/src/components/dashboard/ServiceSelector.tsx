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
    <section className="service-selector">
      <h2 className="service-selector-title">
        Services disponibles
      </h2>
      <div className="service-selector-list scrollbar-thin scrollbar-thumb-indigo-500 scrollbar-track-transparent">
        {services.map((service, i) => {
          const isActive = selectedService?.name === service.name;
          return (
            <button
              key={i}
              onClick={() => onSelect(service)}
              className={`service-selector-button ${isActive ? 'active' : ''}`}
            >
              {service.name}
            </button>
          );
        })}
      </div>
    </section>
  );
};

export default ServiceSelector;
