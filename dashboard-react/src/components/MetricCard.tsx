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
}

export function MetricCard({ title, value, icon: Icon, trend, className = '' }: MetricCardProps) {
  return (
    <div className={`bg-primary-800/50 border border-primary-700 rounded-xl p-6 transition-all duration-200 hover:bg-primary-700/50 hover:border-primary-600 hover:-translate-y-0.5 hover:shadow-lg ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-primary-300 text-sm font-medium mb-1">{title}</p>
          <p className="text-3xl font-bold text-primary-50">{value}</p>
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
        <div className="p-3 rounded-lg bg-primary-700/50">
          <Icon className="h-6 w-6 text-primary-300" />
        </div>
      </div>
    </div>
  );
}
