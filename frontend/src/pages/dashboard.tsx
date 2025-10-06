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
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center">
      <header className="w-full flex flex-col pt-20 items-center mb-8">
        <h1 className="text-6xl font-bold text-center mb-4">Dashboard</h1>
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
