'use client';

import React from 'react';
import { ReadyState } from '@/hooks/useWebSocket';

interface WebSocketStatusProps {
  isConnected: boolean;
  readyState: number;
  connectionAttempts: number;
  className?: string;
}

const getStatusInfo = (readyState: number, isConnected: boolean, attempts: number) => {
  switch (readyState) {
    case ReadyState.UNINSTANTIATED:
      return {
        text: 'Not Connected',
        color: 'text-gray-500',
        bg: 'bg-gray-100',
        icon: '○'
      };
    case ReadyState.CONNECTING:
      return {
        text: attempts > 0 ? `Reconnecting... (${attempts})` : 'Connecting...',
        color: 'text-yellow-600',
        bg: 'bg-yellow-100',
        icon: '◐'
      };
    case ReadyState.OPEN:
      return {
        text: 'Connected',
        color: 'text-green-600',
        bg: 'bg-green-100',
        icon: '●'
      };
    case ReadyState.CLOSING:
      return {
        text: 'Disconnecting...',
        color: 'text-orange-600',
        bg: 'bg-orange-100',
        icon: '◑'
      };
    case ReadyState.CLOSED:
      return {
        text: attempts > 0 ? `Disconnected (Retrying...)` : 'Disconnected',
        color: 'text-red-600',
        bg: 'bg-red-100',
        icon: '○'
      };
    default:
      return {
        text: 'Unknown',
        color: 'text-gray-500',
        bg: 'bg-gray-100',
        icon: '?'
      };
  }
};

export default function WebSocketStatus({ 
  isConnected, 
  readyState, 
  connectionAttempts, 
  className = '' 
}: WebSocketStatusProps) {
  const status = getStatusInfo(readyState, isConnected, connectionAttempts);

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${status.bg} ${status.color} ${className}`}>
      <span className="mr-1" aria-hidden="true">{status.icon}</span>
      <span>{status.text}</span>
    </div>
  );
}
