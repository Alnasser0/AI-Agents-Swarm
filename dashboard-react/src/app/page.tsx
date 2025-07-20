'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { 
  EnvelopeIcon,
  CpuChipIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

import { MetricCard } from '@/components/MetricCard';
import { ModelSelector } from '@/components/ModelSelector';
import { useRealtimeData, useAutoRefresh } from '@/hooks';

interface SyncFormData {
  days: number;
  limit: number;
}

export default function Dashboard() {
  const { isEnabled: autoRefreshEnabled, toggle: toggleAutoRefresh } = useAutoRefresh(true);
  const {
    stats,
    agents,
    tasks,
    logs,
    isConnected,
    error,
    startPolling,
    stopPolling,
  } = useRealtimeData(autoRefreshEnabled, 30000);

  const [showSyncForm, setShowSyncForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors }, reset } = useForm<SyncFormData>({
    defaultValues: {
      days: 7,
      limit: 50
    }
  });

  const onSyncSubmit = async (data: SyncFormData) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/management/sync-past-emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      
      if (response.ok && result.success) {
        alert(`✅ Started syncing past ${data.days} days of emails (limit: ${data.limit})`);
        setShowSyncForm(false);
        reset();
      } else {
        alert(`❌ Failed to sync emails: ${result.message || result.detail}`);
      }
    } catch (err) {
      alert(`❌ Error syncing emails: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncPastEmails = async (days: number, limit: number) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/management/sync-past-emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ days, limit })
      });
      const result = await response.json();
      
      if (response.ok && result.success) {
        alert(`✅ Started syncing past ${days} days of emails (limit: ${limit})`);
      } else {
        alert(`❌ Failed to sync emails: ${result.message || result.detail}`);
      }
    } catch (err) {
      alert(`❌ Error syncing emails: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearData = async () => {
    if (!confirm('⚠️ Are you sure you want to clear all processed email data? This action cannot be undone.')) {
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/management/clear-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      
      if (response.ok && result.success) {
        alert('✅ All processed data cleared successfully');
      } else {
        alert(`❌ Failed to clear data: ${result.message || result.detail}`);
      }
    } catch (err) {
      alert(`❌ Error clearing data: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  const formatUptime = (hours: number): string => {
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    } else if (hours < 24) {
      return `${hours.toFixed(1)}h`;
    } else {
      return `${(hours / 24).toFixed(1)}d`;
    }
  };

  const formatNumber = (num: number | undefined | null): string => {
    if (num === undefined || num === null || isNaN(num)) {
      return '0';
    }
    return num.toLocaleString();
  };

  return (
    <div className="min-h-screen bg-primary-950">
      {/* Header */}
      <header className="border-b border-primary-800 bg-primary-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary-50">
                🤖 AI Agents Swarm
              </h1>
              <p className="text-primary-300 mt-1">
                Automating your workflow with intelligent agents
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleAutoRefresh}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  autoRefreshEnabled
                    ? 'bg-success-600 hover:bg-success-500 text-white'
                    : 'bg-primary-700 hover:bg-primary-600 text-primary-200'
                }`}
                title={autoRefreshEnabled ? "Disable automatic data refresh" : "Enable automatic data refresh"}
                aria-label={autoRefreshEnabled ? "Disable auto-refresh" : "Enable auto-refresh"}
              >
                {autoRefreshEnabled ? '⏸️ Auto-refresh ON' : '▶️ Auto-refresh OFF'}
              </button>
              
              {/* Admin Controls */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowSyncForm(true)}
                  disabled={isLoading}
                  className="px-3 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
                  title="Sync past emails from the last N days with custom email limit"
                  aria-label="Sync past emails with custom parameters"
                >
                  📧 {isLoading ? 'Processing...' : 'Sync Past'}
                </button>
                
                <button
                  onClick={handleClearData}
                  disabled={isLoading}
                  className="px-3 py-2 bg-red-600 hover:bg-red-500 disabled:bg-gray-600 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
                  title="Clear all processed email data and reset the cache (cannot be undone)"
                  aria-label="Clear all processed data"
                >
                  🗑️ {isLoading ? 'Processing...' : 'Clear Data'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-error-900/30 border border-error-700 rounded-lg p-4">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-error-400 mr-3" />
              <div>
                <h3 className="text-error-300 font-medium">Connection Error</h3>
                <p className="text-error-400 text-sm mt-1">{error}</p>
                <p className="text-error-500 text-xs mt-1">Showing mock data for demonstration</p>
              </div>
            </div>
          </div>
        )}

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <MetricCard
            title="📧 Emails Processed"
            value={stats ? formatNumber(stats.emails_processed) : '0'}
            icon={EnvelopeIcon}
            description="Total number of emails processed and analyzed by the system"
          />
          <MetricCard
            title="✅ Tasks Created"
            value={stats ? formatNumber(stats.tasks_created) : '0'}
            icon={CheckCircleIcon}
            description="Total number of tasks successfully created in Notion database"
          />
          <MetricCard
            title="🗃️ Processed Cache"
            value={stats ? formatNumber(stats.processed_emails_count) : '0'}
            icon={CpuChipIcon}
            description="Number of emails cached to prevent duplicate processing"
          />
          <MetricCard
            title="⏰ Uptime"
            value={stats ? formatUptime(stats.uptime_hours) : '0m'}
            icon={ClockIcon}
            description="How long the system has been running since last restart"
          />
          <MetricCard
            title="❌ Errors"
            value={stats ? formatNumber(stats.errors) : '0'}
            icon={ExclamationTriangleIcon}
            description="Total number of errors encountered during processing"
          />
        </div>

        {/* Model Selection */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-primary-50 mb-4 flex items-center">
            🤖 AI Model Selection
          </h2>
          <ModelSelector />
        </div>

        {/* Agent Status */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-primary-50 mb-4 flex items-center">
            🤖 Agent Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, index) => (
              <div key={index} className="card">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-primary-50 flex items-center">
                    <div className={`status-indicator mr-3 ${
                      agent.status === 'online' ? 'status-online' : 
                      agent.status === 'warning' ? 'status-warning' : 'status-offline'
                    }`} />
                    {agent.name}
                  </h3>
                </div>
                <div className="space-y-1 text-sm text-primary-300">
                  {agent.provider && (
                    <div><strong>Provider:</strong> {agent.provider}</div>
                  )}
                  {agent.account && (
                    <div><strong>Account:</strong> {agent.account}</div>
                  )}
                  {agent.interval && (
                    <div><strong>Interval:</strong> {agent.interval}</div>
                  )}
                  {agent.database && (
                    <div><strong>Database:</strong> {agent.database}</div>
                  )}
                  {agent.schema && (
                    <div><strong>Schema:</strong> {agent.schema}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Tasks */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-primary-50 mb-4 flex items-center">
            📋 Recent Tasks
          </h2>
          <div className="card">
            {tasks.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-primary-700">
                      <th className="text-left py-3 px-4 font-medium text-primary-300">Title</th>
                      <th className="text-left py-3 px-4 font-medium text-primary-300">Source</th>
                      <th className="text-left py-3 px-4 font-medium text-primary-300">Priority</th>
                      <th className="text-left py-3 px-4 font-medium text-primary-300">Status</th>
                      <th className="text-left py-3 px-4 font-medium text-primary-300">From</th>
                      <th className="text-left py-3 px-4 font-medium text-primary-300">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => (
                      <tr key={task.id} className="border-b border-primary-800 hover:bg-primary-700/20">
                        <td className="py-3 px-4 text-primary-50">{task.title}</td>
                        <td className="py-3 px-4 text-primary-300">{task.source}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            task.priority === 'High' ? 'bg-error-900/30 text-error-300' :
                            task.priority === 'Medium' ? 'bg-warning-900/30 text-warning-300' :
                            'bg-primary-800 text-primary-300'
                          }`}>
                            {task.priority}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            task.status === 'Done' ? 'bg-success-900/30 text-success-300' :
                            task.status === 'In Progress' ? 'bg-warning-900/30 text-warning-300' :
                            'bg-primary-800 text-primary-300'
                          }`}>
                            {task.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-primary-300">{task.from}</td>
                        <td className="py-3 px-4 text-primary-400 text-sm">
                          {new Date(task.created).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-primary-400">
                No tasks found yet. Tasks will appear here once emails are processed.
              </div>
            )}
          </div>
        </div>

        {/* System Logs */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-primary-50 mb-4 flex items-center">
            📜 System Logs
          </h2>
          <div className="card">
            <div className="log-container">
              {logs.length > 0 ? (
                <div className="space-y-1">
                  {logs.slice().reverse().map((log, index) => (
                    <div
                      key={index}
                      className={`log-entry ${
                        log.level === 'ERROR' ? 'log-entry-error' :
                        log.level === 'WARNING' ? 'log-entry-warning' :
                        log.level === 'INFO' ? 'log-entry-info' :
                        'log-entry-debug'
                      }`}
                    >
                      <span className="text-primary-500 mr-2">
                        [{new Date(log.timestamp).toLocaleTimeString()}]
                      </span>
                      <span className="font-medium mr-2">{log.level}</span>
                      {log.component && (
                        <span className="text-primary-400 mr-2">| {log.component} |</span>
                      )}
                      <span>{log.message}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-primary-400 py-4">
                  No log entries found.
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Sync Form Modal */}
      {showSyncForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-primary-900 border border-primary-700 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-primary-50 mb-4">
              📧 Sync Past Emails
            </h3>
            
            <form onSubmit={handleSubmit(onSyncSubmit)} className="space-y-4">
              <div>
                <label htmlFor="days" className="block text-sm font-medium text-primary-300 mb-2">
                  Past Days
                </label>
                <input
                  type="number"
                  id="days"
                  min="1"
                  max="365"
                  {...register('days', { 
                    required: 'Days is required',
                    min: { value: 1, message: 'Must be at least 1 day' },
                    max: { value: 365, message: 'Cannot exceed 365 days' }
                  })}
                  className="w-full px-3 py-2 bg-primary-800 border border-primary-600 rounded-lg text-primary-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="7"
                />
                {errors.days && (
                  <p className="text-red-400 text-sm mt-1">{errors.days.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="limit" className="block text-sm font-medium text-primary-300 mb-2">
                  Email Limit
                </label>
                <input
                  type="number"
                  id="limit"
                  min="1"
                  max="1000"
                  {...register('limit', { 
                    required: 'Limit is required',
                    min: { value: 1, message: 'Must be at least 1 email' },
                    max: { value: 1000, message: 'Cannot exceed 1000 emails' }
                  })}
                  className="w-full px-3 py-2 bg-primary-800 border border-primary-600 rounded-lg text-primary-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="50"
                />
                {errors.limit && (
                  <p className="text-red-400 text-sm mt-1">{errors.limit.message}</p>
                )}
              </div>

              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowSyncForm(false);
                    reset();
                  }}
                  className="px-4 py-2 text-primary-300 hover:text-primary-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
                >
                  {isLoading ? 'Starting...' : 'Start Sync'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
