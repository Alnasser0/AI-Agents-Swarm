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
}

export function useWebSocket(url: string, enabled: boolean = true): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const isManualClose = useRef(false);
  const connectionAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (!enabled || ws.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    try {
      // Close existing connection if any
      if (ws.current) {
        isManualClose.current = true;
        ws.current.close();
      }

      ws.current = new WebSocket(url);
      connectionAttemptsRef.current += 1;
      setConnectionAttempts(connectionAttemptsRef.current);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        connectionAttemptsRef.current = 0;
        setConnectionAttempts(0);
        isManualClose.current = false;
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        
        // Attempt to reconnect if it wasn't a manual close
        if (!isManualClose.current && enabled) {
          const delay = Math.min(1000 * Math.pow(2, connectionAttemptsRef.current), 30000); // Exponential backoff, max 30s
          console.log(`Attempting to reconnect in ${delay}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [url, enabled]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (ws.current) {
      isManualClose.current = true;
      ws.current.close();
      ws.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }, []);

  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connectionAttempts
  };
}
