/**
 * Metric Card Component - Display key system metrics
 */

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: any; // Will be properly typed once React is installed
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
  description?: string; // Tooltip description
}

export function MetricCard({ title, value, icon: Icon, trend, className = '', description }: MetricCardProps) {
  return (
    <div 
      className={`bg-primary-800/50 border border-primary-700 rounded-xl p-6 transition-all duration-200 hover:bg-primary-700/50 hover:border-primary-600 hover:-translate-y-0.5 hover:shadow-lg group ${className}`}
      title={description}
      aria-label={description}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-primary-300 text-sm font-medium mb-1 group-hover:text-primary-200 transition-colors">
            {title}
            {description && (
              <span className="ml-1 text-xs text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                ℹ️
              </span>
            )}
          </p>
          <p className="text-3xl font-bold text-primary-50 group-hover:text-white transition-colors">{value}</p>
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${
              trend.isPositive ? 'text-success-400' : 'text-error-400'
            }`}>
              <span className="mr-1">
                {trend.isPositive ? '↗' : '↘'}
              </span>
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
        <div className="p-3 rounded-lg bg-primary-700/50 group-hover:bg-primary-600/50 transition-colors">
          <Icon className="h-6 w-6 text-primary-300 group-hover:text-primary-200 transition-colors" />
        </div>
      </div>
      {description && (
        <div className="absolute invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all duration-200 bg-gray-900 text-white text-xs rounded py-2 px-3 -mt-2 transform -translate-y-full left-1/2 -translate-x-1/2 whitespace-nowrap z-10 shadow-lg">
          {description}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  );
}
