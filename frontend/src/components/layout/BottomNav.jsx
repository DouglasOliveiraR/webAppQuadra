import React from 'react';
import { Home, ClipboardList, TrendingUp, Trophy, Wallet } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { cn } from '../ui/Button';

export function BottomNav() {
  const links = [
    { to: '/', icon: Home, label: 'Início' },
    { to: '/ranking', icon: Trophy, label: 'Ranking' },
    { to: '/votos', icon: TrendingUp, label: 'Votação' },
    { to: '/financeiro', icon: Wallet, label: 'Carteira' },
    { to: '/checkin', icon: ClipboardList, label: 'Check-in' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-md border-t border-surface-variant flex justify-around items-center px-4 pb-safe z-50">
      {links.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          aria-label={label}
          className={({ isActive }) => cn(
            "relative flex flex-col items-center justify-center w-full h-full space-y-1 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-standard",
            isActive ? "text-primary" : "text-on-background/60 hover:text-primary/70"
          )}
        >
          {({ isActive }) => (
            <>
              <div className="relative">
                <Icon size={24} strokeWidth={2.5} aria-hidden="true" />
                {isActive && <span className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full" aria-hidden="true" />}
              </div>
              <span className="text-[10px] font-bold tracking-wider max-[359px]:sr-only">{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
