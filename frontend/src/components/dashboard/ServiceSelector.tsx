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
        Available Services
      </h2>
      <div className="service-selector-list scrollbar-thin scrollbar-thumb-indigo-500 scrollbar-track-transparent">
        {services.map((service) => {
          const isActive = selectedService?.name === service.name;
          return (
            <button
              key={service.name}
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
