/**
 * Custom hooks for dashboard data management
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useWebSocket, ReadyState } from './useWebSocket';
import {
  getSystemStats,
  getAgentStatus,
  getRecentTasks,
  getSystemLogs,
  getHealthStatus,
  pingBackend,
  generateMockStats,
  generateMockTasks,
  generateMockLogs,
} from '@/lib/api';
import type {
  SystemStats,
  AgentStatus,
  Task,
  LogEntry,
  HealthResponse,
  UseSystemStats,
  UseRealtimeData,
} from '@/types';

/**
 * Hook for fetching system statistics
 */
export function useSystemStats(refreshInterval: number = 30000): UseSystemStats {
  const [data, setData] = useState<SystemStats | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const fetchStats = useCallback(async () => {
    try {
      setError(null);
      const stats = await getSystemStats();
      setData(stats);
      return stats;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      
      // Fallback to mock data in development or when API is unavailable
      console.warn('API unavailable, using mock data:', error.message);
      const mockStats = generateMockStats();
      setData(mockStats);
      return mockStats;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const mutate = useCallback(() => {
    setIsLoading(true);
    return fetchStats();
  }, [fetchStats]);

  useEffect(() => {
    fetchStats();

    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchStats, refreshInterval]);

  return { data, error, isLoading, mutate };
}

/**
 * Hook for managing real-time dashboard data with WebSocket and polling fallback
 */
export function useRealtimeData(
  autoRefresh: boolean = true,
  refreshInterval: number = 30000
): UseRealtimeData {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);

  // WebSocket connection for real-time updates
  // No need to pass URL - useWebSocket will use environment variables
  const { isConnected: wsConnected, lastMessage, readyState, connectionAttempts } = useWebSocket(undefined, autoRefresh);

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    try {
      switch (lastMessage.type) {
        case 'stats_update':
          setStats(lastMessage.data);
          setIsConnected(true);
          break;
          
        case 'log_update':
          setLogs(prevLogs => {
            const newLogs = [...prevLogs, lastMessage.data];
            // Keep only the latest 50 logs
            return newLogs.slice(-50);
          });
          break;
          
        case 'task_update':
          setTasks(prevTasks => {
            const newTasks = [lastMessage.data, ...prevTasks];
            // Keep only the latest 20 tasks
            return newTasks.slice(0, 20);
          });
          break;
      }
    } catch (err) {
      console.error('Error processing WebSocket message:', err);
    }
  }, [lastMessage]);

  const fetchAllData = useCallback(async () => {
    try {
      setError(null);
      
      // Check if backend is reachable
      const backendReachable = await pingBackend();
      setIsConnected(backendReachable || wsConnected);
      
      if (backendReachable) {
        // Fetch real data from API
        const [statsResult, agentsResult, tasksResult, logsResult] = await Promise.allSettled([
          getSystemStats(),
          getAgentStatus(),
          getRecentTasks(10),
          getSystemLogs(15),
        ]);

        if (statsResult.status === 'fulfilled') {
          setStats(statsResult.value);
        }
        
        if (agentsResult.status === 'fulfilled') {
          setAgents(agentsResult.value);
        }
        
        if (tasksResult.status === 'fulfilled') {
          setTasks(tasksResult.value);
        }
        
        if (logsResult.status === 'fulfilled') {
          setLogs(logsResult.value);
        }
      } else {
        // Use mock data when backend is not available and no WebSocket
        if (!wsConnected) {
          setStats(generateMockStats());
          setAgents([
            {
              name: 'Email Agent',
              status: 'offline',
              provider: 'IMAP',
              account: 'user@example.com',
              interval: '5 minutes',
            },
            {
              name: 'Notion Agent',
              status: 'offline',
              database: 'tasks...',
              schema: '❌ Invalid',
            },
          ]);
          setTasks(generateMockTasks());
          setLogs(generateMockLogs());
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Error fetching dashboard data:', err);
      
      // Still provide mock data on error if no WebSocket
      if (!wsConnected) {
        setStats(generateMockStats());
        setTasks(generateMockTasks());
        setLogs(generateMockLogs());
      }
    }
  }, [wsConnected]);

  const startPolling = useCallback(() => {
    if (isPollingRef.current) return;
    
    isPollingRef.current = true;
    
    // If WebSocket is connected, reduce polling frequency
    const pollInterval = wsConnected ? refreshInterval * 3 : refreshInterval;
    
    fetchAllData(); // Initial fetch
    
    if (pollInterval > 0) {
      intervalRef.current = setInterval(fetchAllData, pollInterval);
    }
  }, [fetchAllData, refreshInterval, wsConnected]);

  const stopPolling = useCallback(() => {
    isPollingRef.current = false;
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Auto-start polling based on autoRefresh setting
  useEffect(() => {
    if (autoRefresh) {
      startPolling();
    } else {
      stopPolling();
    }

    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, [autoRefresh, startPolling, stopPolling]);

  // Update connection status based on WebSocket
  useEffect(() => {
    if (wsConnected) {
      setIsConnected(true);
    } else {
      // If WebSocket is explicitly closed/failed and not just connecting, update connection status
      if (readyState === ReadyState.CLOSED || readyState === ReadyState.CLOSING) {
        setIsConnected(false);
      }
    }
  }, [wsConnected, readyState]);

  return {
    stats,
    agents,
    tasks,
    logs,
    isConnected: isConnected || wsConnected,
    error,
    startPolling,
    stopPolling,
    // WebSocket status information
    wsConnected,
    wsReadyState: readyState,
    wsConnectionAttempts: connectionAttempts,
  };
}

/**
 * Hook for checking system health
 */
export function useHealthCheck(refreshInterval: number = 60000) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setError(null);
      const healthData = await getHealthStatus();
      setHealth(healthData);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Health check failed');
      setError(error);
      
      // Mock health data when API is unavailable
      setHealth({
        status: 'unhealthy',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        services: {
          email: false,
          notion: false,
          ai_model: false,
        },
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    if (refreshInterval > 0) {
      const interval = setInterval(checkHealth, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [checkHealth, refreshInterval]);

  return { health, isLoading, error, refetch: checkHealth };
}

/**
 * Hook for managing auto-refresh state
 */
export function useAutoRefresh(defaultEnabled: boolean = true) {
  const [isEnabled, setIsEnabled] = useState(defaultEnabled);
  const [interval, setInterval] = useState(30000); // 30 seconds default

  const toggle = useCallback(() => {
    setIsEnabled(prev => !prev);
  }, []);

  const enable = useCallback(() => {
    setIsEnabled(true);
  }, []);

  const disable = useCallback(() => {
    setIsEnabled(false);
  }, []);

  const setRefreshInterval = useCallback((newInterval: number) => {
    setInterval(newInterval);
  }, []);

  return {
    isEnabled,
    interval,
    toggle,
    enable,
    disable,
    setRefreshInterval,
  };
}

/**
 * Hook for managing dashboard actions
 */
export function useDashboardActions() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const executeAction = useCallback(async (
    action: () => Promise<any>,
    successMessage?: string
  ) => {
    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);
      
      await action();
      
      if (successMessage) {
        setSuccess(successMessage);
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Action failed';
      setError(errorMessage);
      // Clear error message after 5 seconds
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return {
    isLoading,
    error,
    success,
    executeAction,
    clearMessages,
  };
}
