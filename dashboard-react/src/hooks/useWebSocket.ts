import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: 'stats_update' | 'log_update' | 'task_update';
  data: any;
  timestamp: string;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: any) => void;
  connectionAttempts: number;
  readyState: number;
}

// WebSocket ready states
export enum ReadyState {
  UNINSTANTIATED = -1,
  CONNECTING = 0,
  OPEN = 1,
  CLOSING = 2,
  CLOSED = 3,
}

/**
 * Get WebSocket URL based on environment configuration
 * Uses the same logic as API utilities for consistency
 */
function getWebSocketUrl(): string {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL || 'http://localhost:8000';
  
  // Convert HTTP/HTTPS URL to WebSocket URL
  const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + '/ws';
  
  return wsUrl;
}

export function useWebSocket(url?: string, enabled: boolean = true): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [readyState, setReadyState] = useState<ReadyState>(ReadyState.UNINSTANTIATED);
  
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const isManualClose = useRef(false);
  const connectionAttemptsRef = useRef(0);
  const didUnmount = useRef(false);

  // Use provided URL or get from environment
  const websocketUrl = url || getWebSocketUrl();

  const connect = useCallback(() => {
    if (!enabled || ws.current?.readyState === WebSocket.CONNECTING || didUnmount.current) {
      return;
    }

    try {
      // Close existing connection if any
      if (ws.current) {
        isManualClose.current = true;
        ws.current.close();
      }

      console.log(`Attempting WebSocket connection to: ${websocketUrl}`);
      ws.current = new WebSocket(websocketUrl);
      connectionAttemptsRef.current += 1;
      setConnectionAttempts(connectionAttemptsRef.current);
      setReadyState(ReadyState.CONNECTING);

      ws.current.onopen = () => {
        console.log('WebSocket connected successfully');
        setIsConnected(true);
        setReadyState(ReadyState.OPEN);
        connectionAttemptsRef.current = 0;
        setConnectionAttempts(0);
        isManualClose.current = false;
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error, 'Raw data:', event.data);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
          manual: isManualClose.current
        });
        setIsConnected(false);
        setReadyState(ReadyState.CLOSED);
        
        // Attempt to reconnect if it wasn't a manual close and component is still mounted
        if (!isManualClose.current && enabled && !didUnmount.current) {
          // Exponential backoff with jitter, max 30 seconds
          const baseDelay = Math.min(1000 * Math.pow(2, connectionAttemptsRef.current), 30000);
          const jitter = Math.random() * 1000; // Add up to 1 second of jitter
          const delay = baseDelay + jitter;
          
          console.log(`Attempting to reconnect in ${Math.round(delay)}ms... (attempt ${connectionAttemptsRef.current + 1})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (!didUnmount.current) {
              connect();
            }
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', {
          error,
          url: websocketUrl,
          readyState: ws.current?.readyState,
          attempts: connectionAttemptsRef.current
        });
        setReadyState(ReadyState.CLOSED);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', {
        error,
        url: websocketUrl
      });
      setReadyState(ReadyState.CLOSED);
      
      // Retry after a delay if not manually closed
      if (!isManualClose.current && enabled && !didUnmount.current) {
        const delay = Math.min(5000 * Math.pow(2, connectionAttemptsRef.current), 30000);
        console.log(`Retrying WebSocket connection in ${delay}ms due to creation error...`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          if (!didUnmount.current) {
            connect();
          }
        }, delay);
      }
    }
  }, [websocketUrl, enabled]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (ws.current) {
      isManualClose.current = true;
      setReadyState(ReadyState.CLOSING);
      ws.current.close();
      ws.current = null;
    }
    
    setIsConnected(false);
    setReadyState(ReadyState.CLOSED);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('WebSocket is not connected. Cannot send message. Current state:', readyState);
    }
  }, [readyState]);

  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      didUnmount.current = true;
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      didUnmount.current = true;
    };
  }, []);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connectionAttempts,
    readyState
  };
}
