import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | null;
  subtitle?: string;
}

export default function StatCard({ label, value, icon: Icon, trend, subtitle }: StatCardProps) {
  return (
    <div className="bg-surface-card border border-surface-border rounded-xl p-4">
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-surface-muted uppercase tracking-wider">{label}</p>
        <div className={`p-1.5 rounded-lg ${trend === 'up' ? 'bg-success/10' : trend === 'down' ? 'bg-danger/10' : 'bg-surface'}`}>
          <Icon className={`w-3.5 h-3.5 ${trend === 'up' ? 'text-success' : trend === 'down' ? 'text-danger' : 'text-surface-muted'}`} />
        </div>
      </div>
      <p className={`text-xl font-bold font-mono ${
        trend === 'up' ? 'text-success' : trend === 'down' ? 'text-danger' : 'text-white'
      }`}>
        {value}
      </p>
      {subtitle && <p className="text-xs text-surface-muted mt-1">{subtitle}</p>}
    </div>
  );
}
