/*
** EPITECH PROJECT, 2025
** Area
** File description:
** dashboard
*/

import React, {useState, useEffect} from "react";
import type { Service, User } from "../types";
import { mockServices } from "../data/mockServices";
import { getStoredUser } from "../utils/helper";
import { UserGreeting, ServiceSelector, ServiceDetails, KPIPlaceHolder } from "../components";
import "../styles/dashboard/dashboard.css";

const Dashboard: React.FC = () => {
  // Example state to represent user data
  //
  const [user, setUser] = useState<User | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);

  useEffect(() => {
    // Simulate fetching user data
    setUser(getStoredUser());
    setServices(mockServices);
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>
        <UserGreeting user={user} />
      </header>

      {/* KPI placeholder */}
      <KPIPlaceHolder />

      {/* SERVICE SELECTOR */}
        <ServiceSelector
          services={services}
          selectedService={selectedService}
          onSelect={setSelectedService}
        />

      {/* SERVICE DETAILS */}
        <ServiceDetails service={selectedService} />
    </div>
  );
};

export default Dashboard;
