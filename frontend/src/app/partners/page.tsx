import Sidebar from '@/components/ui/Sidebar';
import { Users, Star, TrendingUp } from 'lucide-react';

const PARTNERS = [
  { name: 'BTCC', description: 'Perpetuals & futures exchange. Testnet validated.', status: 'integrated', logo: '₿' },
  { name: 'Bitget', description: 'Spot & derivatives. CCXT Pro adapter live.', status: 'integrated', logo: 'B' },
  { name: 'Binance', description: 'Coming soon — awaiting testnet validation.', status: 'pending', logo: '⬡' },
];

export default function PartnersPage() {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-brand-400" />
            Exchange Partners
          </h1>
          <p className="text-surface-muted text-sm mt-0.5">Integrated exchanges and broker connections</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {PARTNERS.map((p) => (
            <div key={p.name} className="bg-surface-card border border-surface-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-brand-600/10 border border-brand-600/20 flex items-center justify-center text-2xl">
                  {p.logo}
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                  p.status === 'integrated'
                    ? 'bg-success/10 text-success border border-success/20'
                    : 'bg-warning/10 text-warning border border-warning/20'
                }`}>
                  {p.status === 'integrated' ? '● Integrated' : '○ Pending'}
                </span>
              </div>
              <h3 className="font-bold text-white text-lg">{p.name}</h3>
              <p className="text-surface-muted text-sm mt-1">{p.description}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
