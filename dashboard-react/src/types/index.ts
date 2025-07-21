import { ReactNode } from 'react';

// Core API types
export interface SystemStats {
  emails_processed: number;
  tasks_created: number;  // Changed from tasks_processed to match backend
  processed_emails_count: number;
  uptime_hours: number;
  errors: number;
  realtime_email?: {
    idle_supported: boolean;
    idle_running: boolean;
    idle_thread_alive: boolean;
    status: string;
  };
}

export interface AgentStatus {
  name: string;
  status: 'online' | 'offline' | 'warning';
  provider?: string;
  account?: string;
  interval?: string;
  database?: string;
  schema?: string;
  details?: Record<string, any>;
}

export interface Task {
  id: string;
  title: string;
  source: string;
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  status: 'To Do' | 'In Progress' | 'Done' | 'Cancelled' | 'N/A';
  created: string;
  from: string;
  description?: string;
}

export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'ERROR' | 'WARNING' | 'DEBUG';
  message: string;
  component?: string;
}

export interface RealtimeStatus {
  idle_supported: boolean;
  idle_running: boolean;
  idle_thread_alive: boolean;
  status: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  timestamp: string;
  services: {
    email: boolean;
    notion: boolean;
    ai_model: boolean;
  };
}

// Configuration types
export interface SystemConfiguration {
  email_provider: string;
  email_address: string;
  email_imap_server: string;
  email_check_interval: number;
  notion_database_id: string;
  notion_api_key_configured: boolean;
  default_model: string;
  openai_configured: boolean;
  anthropic_configured: boolean;
}

// Dashboard state types
export interface DashboardState {
  stats: SystemStats | null;
  agents: AgentStatus[];
  tasks: Task[];
  logs: LogEntry[];
  configuration: SystemConfiguration | null;
  health: HealthResponse | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Hook return types
export interface UseSystemStats {
  data: SystemStats | null;
  error: Error | null;
  isLoading: boolean;
  mutate: () => Promise<SystemStats | undefined>;
}

export interface UseRealtimeData {
  stats: SystemStats | null;
  agents: AgentStatus[];
  tasks: Task[];
  logs: LogEntry[];
  isConnected: boolean;
  error: string | null;
  startPolling: () => void;
  stopPolling: () => void;
  // WebSocket status information
  wsConnected: boolean;
  wsReadyState: number;
  wsConnectionAttempts: number;
}

// Component prop types
export interface MetricCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export interface AgentCardProps {
  agent: AgentStatus;
  realtimeStatus?: RealtimeStatus;
}

export interface TaskTableProps {
  tasks: Task[];
  isLoading?: boolean;
}

export interface LogViewerProps {
  logs: LogEntry[];
  maxHeight?: string;
  showControls?: boolean;
}
