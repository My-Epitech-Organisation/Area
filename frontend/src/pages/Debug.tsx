import React, { useState, useEffect } from 'react';
import { triggerDebugAction, getDebugExecutions } from '../services/debugApi';
import type { Area, DebugExecutionsResponse, Execution } from '../types/api';
import { API_BASE } from '../utils/helper';

const Debug: React.FC = () => {
  const [debugAreas, setDebugAreas] = useState<Area[]>([]);
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(null);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [executionDetails, setExecutionDetails] = useState<DebugExecutionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [debugActionId, setDebugActionId] = useState<number | null>(null); // Track debug_manual_trigger action ID

  // Auto-refresh executions every 3 seconds
  useEffect(() => {
    if (!selectedAreaId) return;

    const fetchExecutions = async () => {
      try {
        const data = await getDebugExecutions(selectedAreaId);
        setExecutions(data.executions);
        setExecutionDetails(data);
      } catch (err) {
        console.error('Failed to fetch executions:', err);
      }
    };

    fetchExecutions();
    const interval = setInterval(fetchExecutions, 3000);

    return () => clearInterval(interval);
  }, [selectedAreaId]);

  // Fetch all areas with debug action or debug reaction
  useEffect(() => {
    const fetchDebugAreas = async () => {
      setLoading(true);
      setError(null);

      try {
        const token = localStorage.getItem('access');

        if (!token) {
          throw new Error('Please login to use debug features');
        }

        const response = await fetch(`${API_BASE}/api/areas/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch areas: ${response.statusText}`);
        }

        const data = await response.json();
        const areas: Area[] = data.results || data;

        // Fetch actions and reactions to filter debug areas
        const [actionsResponse, reactionsResponse] = await Promise.all([
          fetch(`${API_BASE}/api/actions/`, {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }),
          fetch(`${API_BASE}/api/reactions/`, {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }),
        ]);

        let filtered: Area[] = [];

        // Filter by debug action (manual trigger)
        if (actionsResponse.ok) {
          const actionsData = await actionsResponse.json();
          const actions = actionsData.results || actionsData;

          const debugAction = actions.find(
            (a: { name: string }) => a.name === 'debug_manual_trigger'
          );

          if (debugAction) {
            setDebugActionId(debugAction.id); // Store the debug action ID
            filtered = areas.filter((area) => area.action === debugAction.id);
          }
        }

        // Also filter by debug reaction (log execution)
        if (reactionsResponse.ok) {
          const reactionsData = await reactionsResponse.json();
          const reactions = reactionsData.results || reactionsData;

          const debugReaction = reactions.find(
            (r: { name: string }) => r.name === 'debug_log_execution'
          );

          if (debugReaction) {
            const areasWithDebugReaction = areas.filter(
              (area) => area.reaction === debugReaction.id
            );
            // Merge both lists, avoiding duplicates
            areasWithDebugReaction.forEach((area) => {
              if (!filtered.find((a) => a.id === area.id)) {
                filtered.push(area);
              }
            });
          }
        }

        setDebugAreas(filtered);

        if (filtered.length > 0 && !selectedAreaId) {
          setSelectedAreaId(filtered[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load debug areas');
      } finally {
        setLoading(false);
      }
    };

    fetchDebugAreas();
  }, [selectedAreaId]);

  const handleTrigger = async (areaId: number) => {
    setTriggering(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await triggerDebugAction(areaId);
      setSuccessMessage(`✓ ${result.message}`);

      // Refresh executions immediately
      if (selectedAreaId === areaId) {
        const data = await getDebugExecutions(areaId);
        setExecutions(data.executions);
        setExecutionDetails(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger action');
    } finally {
      setTriggering(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-400 bg-green-500/10';
      case 'failed':
        return 'text-red-400 bg-red-500/10';
      case 'running':
        return 'text-yellow-400 bg-yellow-500/10';
      case 'pending':
        return 'text-blue-400 bg-blue-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading debug console...</div>
      </div>
    );
  }

  if (debugAreas.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-900 to-purple-900 flex items-center justify-center">
        <div className="text-center max-w-2xl mx-auto p-8 bg-white/5 rounded-xl backdrop-blur-sm border border-white/10">
          <svg
            className="mx-auto h-16 w-16 text-gray-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-2xl font-bold text-white mb-4">No Debug Areas Found</h2>
          <p className="text-gray-300 mb-6">Create an automation with either:</p>
          <ul className="text-left text-gray-300 mb-6 space-y-2 max-w-md mx-auto">
            <li className="flex items-start gap-2">
              <span className="text-indigo-400">•</span>
              <span>
                The{' '}
                <span className="font-mono bg-indigo-500/20 px-2 py-1 rounded text-indigo-300">
                  debug_manual_trigger
                </span>{' '}
                action for manual testing
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-400">•</span>
              <span>
                The{' '}
                <span className="font-mono bg-indigo-500/20 px-2 py-1 rounded text-indigo-300">
                  debug_log_execution
                </span>{' '}
                reaction to log webhook events
              </span>
            </li>
          </ul>
          <a
            href="/Areaction"
            className="inline-block px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
          >
            Create Debug Area
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-900 to-purple-900 pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Test and debug console</h1>
          <p className="text-gray-300">
            Manually trigger actions and monitor executions in real-time
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/50 rounded-lg">
            <p className="text-green-400">{successMessage}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Debug Areas */}
          <div className="bg-white/5 rounded-xl backdrop-blur-sm border border-white/10 p-6">
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              Debug Actions
            </h2>
            <div className="space-y-3">
              {debugAreas.map((area) => (
                <div
                  key={area.id}
                  className={`p-4 rounded-lg border-2 transition cursor-pointer ${
                    selectedAreaId === area.id
                      ? 'bg-indigo-500/20 border-indigo-500'
                      : 'bg-white/5 border-white/10 hover:border-white/30'
                  }`}
                  onClick={() => setSelectedAreaId(area.id)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-medium text-white">{area.name}</h3>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${area.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}
                    >
                      {area.status}
                    </span>
                  </div>

                  {/* Show "Trigger Now" button only for debug_manual_trigger action */}
                  {area.action === debugActionId ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTrigger(area.id);
                      }}
                      disabled={triggering || area.status !== 'active'}
                      className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition font-medium"
                    >
                      {triggering ? 'Triggering...' : '⚡ Trigger Now'}
                    </button>
                  ) : (
                    <div className="text-sm text-gray-400 italic">
                      Triggered by external events
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right: Execution Log */}
          <div className="bg-white/5 rounded-xl backdrop-blur-sm border border-white/10 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Execution Log
              </h2>
              <span className="text-xs text-gray-400">Auto-refresh: 3s</span>
            </div>

            {executionDetails && (
              <div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="text-sm text-gray-400">
                  <div>
                    <span className="font-medium text-white">Area:</span>{' '}
                    {executionDetails.area_name}
                  </div>
                  <div>
                    <span className="font-medium text-white">Action:</span>{' '}
                    {executionDetails.action}
                  </div>
                  <div>
                    <span className="font-medium text-white">Reaction:</span>{' '}
                    {executionDetails.reaction}
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {executions.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <svg
                    className="mx-auto h-12 w-12 mb-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p>No executions yet</p>
                  <p className="text-sm mt-1">Trigger an action to see execution logs</p>
                </div>
              ) : (
                executions.map((execution) => (
                  <div
                    key={execution.id}
                    className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(execution.status)}`}
                      >
                        {execution.status.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatDate(execution.created_at)} {formatTimestamp(execution.created_at)}
                      </span>
                    </div>

                    {execution.reaction_result && (
                      <div className="mt-2 p-2 bg-black/20 rounded border border-white/5">
                        <div className="text-xs text-gray-400 mb-1">Reaction Result:</div>
                        <pre className="text-xs text-gray-300 overflow-x-auto">
                          {JSON.stringify(execution.reaction_result, null, 2)}
                        </pre>
                      </div>
                    )}

                    {execution.error_message && (
                      <div className="mt-2 p-2 bg-red-500/10 rounded border border-red-500/30">
                        <div className="text-xs text-red-400">Error: {execution.error_message}</div>
                      </div>
                    )}

                    {execution.completed_at && (
                      <div className="mt-2 text-xs text-gray-400">
                        Completed at: {formatTimestamp(execution.completed_at)}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Debug;
