'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Terminal,
  Settings,
  Users,
  BookOpen,
  TrendingUp,
  Shield,
  LogOut,
} from 'lucide-react';

const NAV = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/command-center', icon: Terminal, label: 'Command Center' },
  { href: '/education', icon: BookOpen, label: 'Education' },
  { href: '/partners', icon: Users, label: 'Partners' },
  { href: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-16 lg:w-56 flex flex-col bg-surface-card border-r border-surface-border min-h-screen">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-surface-border">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center shrink-0">
          <TrendingUp className="w-4 h-4 text-white" />
        </div>
        <span className="hidden lg:block font-bold text-white text-sm">CryptoSignal</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-2 space-y-1">
        {NAV.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                active
                  ? 'bg-brand-600/15 text-brand-400 font-medium'
                  : 'text-surface-muted hover:text-white hover:bg-surface'
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="hidden lg:block text-sm">{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Guardian indicator */}
      <div className="p-2 border-t border-surface-border">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-surface">
          <Shield className="w-4 h-4 text-brand-400 shrink-0" />
          <div className="hidden lg:block">
            <p className="text-xs font-medium text-white">Guardian</p>
            <p className="text-xs text-surface-muted">Active</p>
          </div>
        </div>
      </div>

      {/* Sign out */}
      <div className="p-2 pb-4">
        <button
          onClick={() => fetch('/api/auth/signout', { method: 'POST' }).then(() => window.location.href = '/auth')}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-surface-muted hover:text-white hover:bg-surface transition-colors w-full"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          <span className="hidden lg:block text-sm">Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
