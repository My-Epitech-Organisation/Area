import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useActions, useReactions, useCreateArea } from "../hooks/useApi";
import { findActionByName, findReactionByName, generateAreaName } from "../utils/areaHelpers";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8080";

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
  logo?: string;
  actions: ServiceAction[];
  reactions: ServiceReaction[];
};

const Areaction: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const preselectedService = queryParams.get('service');
  const preselectedAction = queryParams.get('action');
  const preselectedReaction = queryParams.get('reaction');

  // Fetch actions and reactions from API
  const { data: apiActions, loading: loadingActions, error: errorActions } = useActions();
  const { data: apiReactions, loading: loadingReactions, error: errorReactions } = useReactions();
  const { createArea, loading: creatingArea } = useCreateArea();

  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedActionService, setSelectedActionService] = useState<string | null>(null);
  const [selectedReactionService, setSelectedReactionService] = useState<string | null>(null);
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [selectedReaction, setSelectedReaction] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<'error' | 'success' | null>(null);

  const getServiceByName = (name: string | null): Service | undefined => {
    if (!name) return undefined;
    return services.find(s => s.name.toLowerCase() === name.toLowerCase());
  };

  const getActionsForService = (serviceName: string | null): ServiceAction[] => {
    const service = getServiceByName(serviceName);
    return service?.actions || [];
  };

  const getReactionsForService = (serviceName: string | null): ServiceReaction[] => {
    const service = getServiceByName(serviceName);
    return service?.reactions || [];
  };

  const imageModules = import.meta.glob("../assets/*.{png,jpg,jpeg,svg,gif}", { eager: true }) as Record<string, { default: string }>;
  const imagesByName: Record<string, string> = {};

  Object.keys(imageModules).forEach((p) => {
    const parts = p.split("/");
    const file = parts[parts.length - 1];
    const name = file.replace(/\.[^/.]+$/, "").toLowerCase();
    imagesByName[name] = (imageModules as any)[p].default;
  });

  const resolveLogo = (rawLogo: string | null | undefined, name: string): string | null => {
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
    const fetchServices = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/about.json`);
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        const serviceList: Service[] = data?.server?.services || [];

        setServices(serviceList);

        if (preselectedService) {
          const service = serviceList.find(s =>
            s.name.toLowerCase() === preselectedService.toLowerCase()
          );

          if (service) {
            // Only set as action service if it has actions
            if (service.actions && service.actions.length > 0) {
              setSelectedActionService(service.name);
              if (!preselectedAction && service.actions.length > 0) {
                setSelectedAction(service.actions[0].name);
              } else if (preselectedAction) {
                // Make sure the preselectedAction exists in this service
                const actionExists = service.actions.some(a => a.name === preselectedAction);
                if (actionExists) {
                  setSelectedAction(preselectedAction);
                } else {
                  setSelectedAction(service.actions[0].name);
                }
              }
            }

            // Only set as reaction service if it has reactions
            if (service.reactions && service.reactions.length > 0) {
              setSelectedReactionService(service.name);
              if (!preselectedReaction && service.reactions.length > 0) {
                setSelectedReaction(service.reactions[0].name);
              } else if (preselectedReaction) {
                // Make sure the preselectedReaction exists in this service
                const reactionExists = service.reactions.some(r => r.name === preselectedReaction);
                if (reactionExists) {
                  setSelectedReaction(preselectedReaction);
                } else {
                  setSelectedReaction(service.reactions[0].name);
                }
              }
            }
          }
        }

        setError(null);
      } catch (e: any) {
        setError(e.message || "Failed to load services");
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, [preselectedService, preselectedAction, preselectedReaction]);

  const handleActionServiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const serviceName = e.target.value;
    setSelectedActionService(serviceName);
    setMessage(null);
    setMessageType(null);

    const actions = getActionsForService(serviceName);
    setSelectedAction(actions.length > 0 ? actions[0].name : null);
  };

  const handleReactionServiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const serviceName = e.target.value;
    setSelectedReactionService(serviceName);
    setMessage(null);
    setMessageType(null);

    const reactions = getReactionsForService(serviceName);
    setSelectedReaction(reactions.length > 0 ? reactions[0].name : null);
  };

  const handleCreateAutomation = async () => {
    const missingFields: string[] = [];
    if (!selectedActionService)
        missingFields.push("Action Service");
    if (!selectedAction)
        missingFields.push("Action");
    if (!selectedReactionService)
        missingFields.push("Reaction Service");
    if (!selectedReaction)
        missingFields.push("Reaction");
    if (missingFields.length > 0) {
      setMessage("Please select: " + missingFields.join(", "));
      setMessageType('error');
      return;
    }

    // Find the actual Action and Reaction objects from API
    const actionObj = findActionByName(apiActions || [], selectedAction!);
    const reactionObj = findReactionByName(apiReactions || [], selectedReaction!);

    if (!actionObj) {
      setMessage(`Action "${selectedAction}" not found in database`);
      setMessageType('error');
      return;
    }

    if (!reactionObj) {
      setMessage(`Reaction "${selectedReaction}" not found in database`);
      setMessageType('error');
      return;
    }

    try {
      // Create the AREA with proper payload
      await createArea({
        name: generateAreaName(selectedAction!, selectedReaction!),
        action: actionObj.id,
        reaction: reactionObj.id,
        action_config: {},
        reaction_config: {},
        status: 'active'
      });

      setMessage("Automation created successfully!");
      setMessageType('success');

      // Redirect to dashboard after 1.5 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err: any) {
      setMessage(err.message || "Failed to create automation");
      setMessageType('error');
    }
  };

  const formatName = (name: string): string => {
    return name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  // Combine loading states
  const isLoading = loading || loadingActions || loadingReactions;
  
  // Combine error states
  const combinedError = error || errorActions || errorReactions;

  if (isLoading) {
    return (
      <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
        <p className="text-white mt-4">Loading services...</p>
      </div>
    );
  }

  if (combinedError) {
    return (
      <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Error</h2>
          <p className="text-rose-300">{combinedError}</p>
          <button
            onClick={() => navigate("/services")}
            className="mt-6 inline-block px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
          >
            Back to Services
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-screen min-h-screen bg-page-areaction flex flex-col items-center p-6">
      <header className="w-full pt-20 flex flex-col items-center">
        <h1 className="text-4xl font-bold text-white">Create Automation</h1>
        <p className="text-gray-300 mt-2">Connect actions and reactions to automate your workflow</p>
      </header>

      <main className="w-full max-w-5xl mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-indigo-600 p-3 rounded-xl">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white">When this happens...</h2>
            </div>
            <div className="space-y-6">
              <div>
                <label htmlFor="actionService" className="block text-sm font-medium text-gray-300 mb-2">
                  Choose a service
                </label>
                <div className="relative">
                  <select
                    id="actionService"
                    value={selectedActionService || ""}
                    onChange={handleActionServiceChange}
                    className="block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="" disabled>Select a service</option>
                    {services.filter(s => s.actions && s.actions.length > 0).map((service) => (
                      <option key={`action-service-${service.name}`} value={service.name}>
                        {service.name.charAt(0).toUpperCase() + service.name.slice(1)}
                      </option>
                    ))}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-300">
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>

              {selectedActionService && (
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <label htmlFor="action" className="block text-sm font-medium text-gray-300">
                      Choose a trigger
                    </label>
                    {selectedActionService && (
                      <div className="flex items-center gap-1 bg-indigo-600/20 px-2 py-1 rounded-full">
                        {resolveLogo(getServiceByName(selectedActionService)?.logo, selectedActionService) && (
                          <img
                            src={resolveLogo(getServiceByName(selectedActionService)?.logo, selectedActionService) || ''}
                            alt={selectedActionService}
                            className="h-4 w-4 object-contain"
                          />
                        )}
                        <span className="text-xs text-indigo-300">{selectedActionService}</span>
                      </div>
                    )}
                  </div>
                  <div className="relative">
                    <select
                      id="action"
                      value={selectedAction || ""}
                      onChange={(e) => setSelectedAction(e.target.value)}
                      className="block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      disabled={!selectedActionService}
                    >
                      <option value="" disabled>Select a trigger</option>
                      {getActionsForService(selectedActionService).map((action) => (
                        <option key={`action-${action.name}`} value={action.name}>
                          {formatName(action.name)}
                        </option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-300">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>

                  {selectedAction && getActionsForService(selectedActionService).find(a => a.name === selectedAction)?.description && (
                    <p className="mt-2 text-sm text-gray-400">
                      {getActionsForService(selectedActionService).find(a => a.name === selectedAction)?.description}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-purple-600 p-3 rounded-xl">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white">Then do this...</h2>
            </div>

            <div className="space-y-6">
              <div>
                <label htmlFor="reactionService" className="block text-sm font-medium text-gray-300 mb-2">
                  Choose a service
                </label>
                <div className="relative">
                  <select
                    id="reactionService"
                    value={selectedReactionService || ""}
                    onChange={handleReactionServiceChange}
                    className="block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="" disabled>Select a service</option>
                    {services.filter(s => s.reactions && s.reactions.length > 0).map((service) => (
                      <option key={`reaction-service-${service.name}`} value={service.name}>
                        {service.name.charAt(0).toUpperCase() + service.name.slice(1)}
                      </option>
                    ))}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-300">
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>

              {selectedReactionService && (
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <label htmlFor="reaction" className="block text-sm font-medium text-gray-300">
                      Choose an action
                    </label>
                    {selectedReactionService && (
                      <div className="flex items-center gap-1 bg-purple-600/20 px-2 py-1 rounded-full">
                        {resolveLogo(getServiceByName(selectedReactionService)?.logo, selectedReactionService) && (
                          <img
                            src={resolveLogo(getServiceByName(selectedReactionService)?.logo, selectedReactionService) || ''}
                            alt={selectedReactionService}
                            className="h-4 w-4 object-contain"
                          />
                        )}
                        <span className="text-xs text-purple-300">{selectedReactionService}</span>
                      </div>
                    )}
                  </div>
                  <div className="relative">
                    <select
                      id="reaction"
                      value={selectedReaction || ""}
                      onChange={(e) => setSelectedReaction(e.target.value)}
                      className="block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      disabled={!selectedReactionService}
                    >
                      <option value="" disabled>Select an action</option>
                      {getReactionsForService(selectedReactionService).map((reaction) => (
                        <option key={`reaction-${reaction.name}`} value={reaction.name}>
                          {formatName(reaction.name)}
                        </option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-300">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>

                  {selectedReaction && getReactionsForService(selectedReactionService).find(r => r.name === selectedReaction)?.description && (
                    <p className="mt-2 text-sm text-gray-400">
                      {getReactionsForService(selectedReactionService).find(r => r.name === selectedReaction)?.description}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {selectedActionService && selectedReactionService && selectedAction && selectedReaction && (
          <div className="my-10 p-6 bg-white/5 rounded-xl backdrop-blur-sm">
            <h3 className="text-xl font-medium text-white mb-4">Your automation</h3>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 p-4">
              <div className="flex items-center gap-2 bg-indigo-600/20 px-4 py-3 rounded-lg">
                {resolveLogo(getServiceByName(selectedActionService)?.logo, selectedActionService) && (
                  <img
                    src={resolveLogo(getServiceByName(selectedActionService)?.logo, selectedActionService) || ''}
                    alt={selectedActionService}
                    className="h-6 w-6 object-contain"
                  />
                )}
                <span className="text-indigo-200">{formatName(selectedAction)}</span>
              </div>

              <div className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>

              <div className="flex items-center gap-2 bg-purple-600/20 px-4 py-3 rounded-lg">
                {resolveLogo(getServiceByName(selectedReactionService)?.logo, selectedReactionService) && (
                  <img
                    src={resolveLogo(getServiceByName(selectedReactionService)?.logo, selectedReactionService) || ''}
                    alt={selectedReactionService}
                    className="h-6 w-6 object-contain"
                  />
                )}
                <span className="text-purple-200">{formatName(selectedReaction)}</span>
              </div>
            </div>
          </div>
        )}

        {message && (
          <div className={`w-full max-w-5xl mx-auto mb-4 px-6 py-3 rounded ${messageType === 'error' ? 'text-red-400 bg-red-900/20' : 'text-emerald-300 bg-emerald-900/20'}`}>
            {message}
          </div>
        )}

        <div className="mt-10 flex justify-center">
          <button
            onClick={handleCreateAutomation}
            disabled={!selectedActionService || !selectedReactionService || !selectedAction || !selectedReaction || creatingArea}
            className={`px-8 py-4 rounded-xl font-medium flex items-center gap-2 transition-colors ${
              (!selectedActionService || !selectedReactionService || !selectedAction || !selectedReaction || creatingArea)
                ? 'bg-gray-600 text-gray-300 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white'
            }`}
          >
            {creatingArea ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                Creating...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Create Automation
              </>
            )}
          </button>
        </div>
      </main>
    </div>
  );
};

export default Areaction;
