'use client';

import { useState, useEffect } from 'react';
import { 
  CpuChipIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  available: boolean;
  status: 'available' | 'unavailable';
}

interface ModelsByProvider {
  [provider: string]: ModelInfo[];
}

interface ModelsData {
  models: ModelsByProvider;
  current_model: string | null;
}

interface CurrentModelInfo {
  model: string;
  available: boolean;
  status: 'available' | 'unavailable';
}

export function ModelSelector() {
  const [modelsData, setModelsData] = useState<ModelsData | null>(null);
  const [currentModel, setCurrentModel] = useState<CurrentModelInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSwitching, setIsSwitching] = useState(false);
  const [showSelector, setShowSelector] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = async () => {
    try {
      setError(null);
      const response = await fetch('/api/models/available');
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.statusText}`);
      }
      const data = await response.json();
      setModelsData(data);
    } catch (err) {
      console.error('Error fetching models:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const fetchCurrentModel = async () => {
    try {
      const response = await fetch('/api/models/current');
      if (!response.ok) {
        throw new Error(`Failed to fetch current model: ${response.statusText}`);
      }
      const data = await response.json();
      setCurrentModel(data);
    } catch (err) {
      console.error('Error fetching current model:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const switchModel = async (modelId: string) => {
    if (!modelId || isSwitching) return;
    
    setIsSwitching(true);
    try {
      const response = await fetch('/api/models/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelId })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${result.message}`);
        setShowSelector(false);
        // Refresh current model info
        await fetchCurrentModel();
        await fetchModels();
      } else {
        alert(`❌ Failed to switch model: ${result.message}`);
      }
    } catch (err) {
      alert(`❌ Error switching model: ${err}`);
    } finally {
      setIsSwitching(false);
    }
  };

  const refreshData = async () => {
    setIsLoading(true);
    await Promise.all([fetchModels(), fetchCurrentModel()]);
    setIsLoading(false);
  };

  useEffect(() => {
    refreshData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'text-green-400';
      case 'unavailable':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircleIcon className="h-4 w-4 text-green-400" />;
      case 'unavailable':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-400" />;
      default:
        return <ExclamationTriangleIcon className="h-4 w-4 text-gray-400" />;
    }
  };

  const getProviderDisplayName = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai':
        return '🤖 OpenAI';
      case 'anthropic':
        return '🧠 Anthropic';
      case 'google':
        return '🟢 Google';
      default:
        return provider;
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center space-x-2">
          <ArrowPathIcon className="h-5 w-5 text-primary-400 animate-spin" />
          <span className="text-primary-300">Loading models...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <span className="text-red-300">Error loading models: {error}</span>
          </div>
          <button
            onClick={refreshData}
            className="px-3 py-1 bg-primary-600 hover:bg-primary-500 text-white rounded text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Current Model Display */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CpuChipIcon className="h-6 w-6 text-primary-400" />
            <div>
              <h3 className="font-medium text-primary-50">Current AI Model</h3>
              {currentModel ? (
                <div className="flex items-center space-x-2 mt-1">
                  {getStatusIcon(currentModel.status)}
                  <span className={`font-mono text-sm ${getStatusColor(currentModel.status)}`}>
                    {currentModel.model}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    currentModel.available 
                      ? 'bg-green-900/30 text-green-300' 
                      : 'bg-red-900/30 text-red-300'
                  }`}>
                    {currentModel.available ? 'Available' : 'Unavailable'}
                  </span>
                </div>
              ) : (
                <span className="text-primary-400 text-sm">No model selected</span>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={refreshData}
              className="p-2 text-primary-400 hover:text-primary-200 transition-colors"
              title="Refresh model status"
            >
              <ArrowPathIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => setShowSelector(!showSelector)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              {showSelector ? 'Hide Models' : 'Switch Model'}
            </button>
          </div>
        </div>
      </div>

      {/* Model Selector */}
      {showSelector && modelsData && (
        <div className="card">
          <h4 className="font-medium text-primary-50 mb-4">Available Models</h4>
          
          <div className="space-y-4">
            {Object.entries(modelsData.models).map(([provider, models]) => (
              <div key={provider} className="border border-primary-700 rounded-lg p-4">
                <h5 className="font-medium text-primary-200 mb-3 flex items-center">
                  {getProviderDisplayName(provider)}
                  <span className="ml-2 text-xs text-primary-500">
                    ({models.length} models)
                  </span>
                </h5>
                
                <div className="space-y-2">
                  {models.map((model) => (
                    <div
                      key={model.id}
                      className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                        model.id === currentModel?.model
                          ? 'border-blue-500 bg-blue-900/20'
                          : model.available
                          ? 'border-primary-600 hover:border-primary-500 hover:bg-primary-700/20 cursor-pointer'
                          : 'border-primary-700 bg-primary-800/30 opacity-60'
                      }`}
                      onClick={() => model.available && model.id !== currentModel?.model && switchModel(model.id)}
                    >
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(model.status)}
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className={`font-mono text-sm ${
                              model.id === currentModel?.model ? 'text-blue-300' : 'text-primary-200'
                            }`}>
                              {model.name}
                            </span>
                            {model.id === currentModel?.model && (
                              <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                                Current
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-primary-400">
                            {model.id}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded ${
                          model.available 
                            ? 'bg-green-900/30 text-green-300' 
                            : 'bg-red-900/30 text-red-300'
                        }`}>
                          {model.available ? 'Available' : 'Unavailable'}
                        </span>
                        
                        {model.available && model.id !== currentModel?.model && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              switchModel(model.id);
                            }}
                            disabled={isSwitching}
                            className="px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:opacity-50 text-white rounded text-xs font-medium transition-colors"
                          >
                            {isSwitching ? 'Switching...' : 'Switch'}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          {isSwitching && (
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
              <div className="flex items-center space-x-2">
                <ArrowPathIcon className="h-4 w-4 text-blue-400 animate-spin" />
                <span className="text-blue-300 text-sm">Switching model...</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
