/*
** EPITECH PROJECT, 2025
** Area
** File description:
** ServiceList
*/

import React from "react";
import type { Service } from "../../types";
import ServiceCard from "./ServiceCard";

interface ServiceListProps {
  services: Service[];
}

const ServiceList: React.FC<ServiceListProps> = ({ services }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {services.map((service) => (
        <ServiceCard key={service.name} service={service} />
      ))}
    </div>
  );
};

export default ServiceList;
