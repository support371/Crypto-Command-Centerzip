import Sidebar from '@/components/ui/Sidebar';
import { BookOpen, ShieldCheck, AlertTriangle, TrendingUp } from 'lucide-react';

const ARTICLES = [
  {
    icon: ShieldCheck,
    title: 'Capital Protection First',
    description: 'Guardian bot provides absolute override. All risk limits are hard-enforced regardless of signal strength.',
    tag: 'Risk Management',
  },
  {
    icon: AlertTriangle,
    title: 'Testnet Validation Protocol',
    description: 'Every strategy must pass testnet validation before live capital is exposed. No exceptions.',
    tag: 'Protocol',
  },
  {
    icon: TrendingUp,
    title: 'Understanding Signal Confidence',
    description: 'Prediction bot outputs a 0–1 confidence score. Only signals above the configured threshold are executed.',
    tag: 'Signals',
  },
  {
    icon: BookOpen,
    title: 'Kill-Switch Mechanics',
    description: 'Auto-triggered at configurable drawdown threshold. Closes all positions, halts execution, sends audit event.',
    tag: 'Kill-Switch',
  },
];

export default function EducationPage() {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-brand-400" />
            Education
          </h1>
          <p className="text-surface-muted text-sm mt-0.5">Platform documentation and trading principles</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ARTICLES.map((a) => {
            const Icon = a.icon;
            return (
              <div key={a.title} className="bg-surface-card border border-surface-border rounded-xl p-5 hover:border-brand-600/40 transition-colors cursor-pointer">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-brand-600/10">
                    <Icon className="w-4 h-4 text-brand-400" />
                  </div>
                  <span className="text-xs font-semibold text-brand-400 uppercase tracking-wider">{a.tag}</span>
                </div>
                <h3 className="font-semibold text-white mb-2">{a.title}</h3>
                <p className="text-surface-muted text-sm leading-relaxed">{a.description}</p>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
