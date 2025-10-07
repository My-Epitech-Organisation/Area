import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

type ServiceAction = {
  name: string;
  description: string;
};

type ServiceReaction = {
  name: string;
  description: string;
};

type Service = {
  name: string;
  logo: string;
  actions: ServiceAction[];
  reactions: ServiceReaction[];
};

const ServiceDetail: React.FC = () => {
  const { serviceId } = useParams<{ serviceId: string }>();
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Lazy load images
  const imageModules = import.meta.glob("../assets/*.{png,jpg,jpeg,svg,gif}", { eager: true }) as Record<string, { default: string }>;
  const imagesByName: Record<string, string> = {};
  
  Object.keys(imageModules).forEach((p) => {
    const parts = p.split("/");
    const file = parts[parts.length - 1];
    const name = file.replace(/\.[^/.]+$/, "").toLowerCase();
    imagesByName[name] = (imageModules as any)[p].default;
  });

  const resolveLogo = (rawLogo: string | null, name: string): string | null => {
    if (rawLogo) {
      if (/^(https?:)?\/\//.test(rawLogo) || rawLogo.startsWith("/")) {
        return rawLogo;
      }
      const base = rawLogo.split("/").pop()?.replace(/\.[^/.]+$/, "").toLowerCase() ?? "";
      if (imagesByName[base]) return imagesByName[base];
    }
    
    const key = name.toLowerCase();
    return imagesByName[key] ?? null;
  };

  useEffect(() => {
    const fetchServiceDetails = async () => {
      setLoading(true);
      try {
        const res = await fetch("/about.json");
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        
        const data = await res.json();
        const serviceList = data?.server?.services || [];
        
        const foundService = serviceList.find((s: any) => 
          (s.id?.toString() === serviceId || s.name?.toLowerCase() === serviceId?.toLowerCase())
        );
        
        if (foundService) {
          setService(foundService);
          setError(null);
        } else {
          setError("Service not found");
        }
      } catch (e: any) {
        setError(e.message || "Failed to load service details");
      } finally {
        setLoading(false);
      }
    };
    
    fetchServiceDetails();
  }, [serviceId]);

  if (loading) {
    return (
      <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center justify-center p-6">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
        <p className="text-white mt-4">Loading service details...</p>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Error</h2>
          <p className="text-rose-300">{error || "Service not found"}</p>
          <Link to="/services" className="mt-6 inline-block px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition">
            Back to Services
          </Link>
        </div>
      </div>
    );
  }

  const logo = resolveLogo(service.logo, service.name);

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 p-6">
      <div className="max-w-6xl mx-auto pt-20">
        <Link to="/services" className="text-indigo-300 hover:text-indigo-100 flex items-center gap-2 mb-8 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          Back to services
        </Link>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 shadow-xl">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            <div className="w-32 h-32 bg-white/10 rounded-xl flex items-center justify-center overflow-hidden p-2">
              {logo ? (
                <img 
                  src={logo} 
                  alt={`${service.name} logo`}
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-4xl font-bold text-white">{service.name.charAt(0).toUpperCase()}</span>
              )}
            </div>

            <div className="flex-1">
              <h1 className="text-3xl md:text-4xl font-bold text-white text-center md:text-left">
                {service.name.charAt(0).toUpperCase() + service.name.slice(1)}
              </h1>
              
              <div className="mt-8 grid gap-8 md:grid-cols-2">
                <div>
                  <h2 className="text-xl font-semibold text-indigo-300 mb-4 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Actions
                  </h2>
                  {service.actions && service.actions.length > 0 ? (
                    <div className="space-y-3">
                      {service.actions.map((action, index) => (
                        <div 
                          key={`action-${index}`} 
                          className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition"
                        >
                          <h3 className="font-medium text-white">{action.name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</h3>
                          <p className="text-sm text-gray-300 mt-1">{action.description}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No actions available</p>
                  )}
                </div>
                
                <div>
                  <h2 className="text-xl font-semibold text-indigo-300 mb-4 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Reactions
                  </h2>
                  {service.reactions && service.reactions.length > 0 ? (
                    <div className="space-y-3">
                      {service.reactions.map((reaction, index) => (
                        <div 
                          key={`reaction-${index}`} 
                          className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition"
                        >
                          <h3 className="font-medium text-white">{reaction.name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</h3>
                          <p className="text-sm text-gray-300 mt-1">{reaction.description}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No reactions available</p>
                  )}
                </div>
              </div>

              <div className="mt-10 flex justify-center md:justify-start">
                <button 
                  className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium flex items-center gap-2 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                  Add Automation with this Service
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetail;