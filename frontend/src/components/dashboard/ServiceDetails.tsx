/*
** EPITECH PROJECT, 2025
** Area
** File description:
** ServiceDetails
*/

import React from "react";
import type { ServiceCardProps } from "../../types";

const ServiceDetails: React.FC<ServiceCardProps> = ({ service }) => {
    if (!service) {
      return (
          <div className="service-details service-details-no-service">
              No service selected
          </div>
      );
    }

    return (
    <div className="service-details">
      <h3 className="service-details-title">{service.name}</h3>

      <div className="service-details-section">
        <h4 className="service-details-section-title">
            Actions
        </h4>
        <ul className="service-details-list">
          {service.actions.map((a, i) => (
            <li key={i}>
              <strong>{a.name}</strong> — {a.description}
            </li>
          ))}
        </ul>
      </div>

      <div className="service-details-section">
        <h4 className="service-details-section-title">
            Reactions
        </h4>
        <ul className="service-details-list">
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
