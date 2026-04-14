'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Shield, Activity, DollarSign, Zap, AlertTriangle, BarChart2 } from 'lucide-react';
import Sidebar from '@/components/ui/Sidebar';
import StatCard from '@/components/ui/StatCard';
import PositionsTable from '@/components/trading/PositionsTable';
import SignalFeed from '@/components/trading/SignalFeed';
import EquityChart from '@/components/charts/EquityChart';
import GuardianStatus from '@/components/trading/GuardianStatus';

export default function DashboardPage() {
  const [systemStatus, setSystemStatus] = useState<'live' | 'testnet' | 'paper' | 'offline'>('paper');
  const [accountData, setAccountData] = useState({
    balance: 0,
    equity: 0,
    unrealizedPnL: 0,
    dailyPnL: 0,
    openPositions: 0,
    totalTrades: 0,
  });

  useEffect(() => {
    async function fetchAccount() {
      try {
        const res = await fetch('/api/account/summary');
        if (res.ok) {
          const data = await res.json();
          setAccountData(data);
          setSystemStatus(data.mode || 'paper');
        }
      } catch {
        // execution core may not be running yet
      }
    }
    fetchAccount();
    const interval = setInterval(fetchAccount, 5000);
    return () => clearInterval(interval);
  }, []);

  const stats = [
    {
      label: 'Account Balance',
      value: `$${accountData.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      icon: DollarSign,
      trend: null,
    },
    {
      label: 'Daily P&L',
      value: `${accountData.dailyPnL >= 0 ? '+' : ''}$${accountData.dailyPnL.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      icon: accountData.dailyPnL >= 0 ? TrendingUp : TrendingDown,
      trend: accountData.dailyPnL >= 0 ? 'up' : 'down',
    },
    {
      label: 'Open Positions',
      value: accountData.openPositions.toString(),
      icon: BarChart2,
      trend: null,
    },
    {
      label: 'Unrealized P&L',
      value: `${accountData.unrealizedPnL >= 0 ? '+' : ''}$${accountData.unrealizedPnL.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      icon: Activity,
      trend: accountData.unrealizedPnL >= 0 ? 'up' : 'down',
    },
  ];

  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Command Center</h1>
            <p className="text-surface-muted text-sm mt-0.5">Real-time trading overview</p>
          </div>
          <div className="flex items-center gap-3">
            <GuardianStatus />
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border ${
              systemStatus === 'live'
                ? 'bg-danger/10 border-danger text-danger'
                : systemStatus === 'testnet'
                ? 'bg-warning/10 border-warning text-warning'
                : 'bg-brand-600/10 border-brand-500 text-brand-400'
            }`}>
              <span className="live-dot" style={systemStatus === 'paper' ? { background: '#64748b', boxShadow: 'none' } : {}} />
              {systemStatus.toUpperCase()}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {stats.map((stat) => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
          <div className="xl:col-span-2">
            <EquityChart />
          </div>
          <div>
            <SignalFeed />
          </div>
        </div>

        {/* Positions */}
        <PositionsTable />
      </main>
    </div>
  );
}
