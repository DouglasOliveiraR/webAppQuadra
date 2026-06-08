import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../ui/Button';

export function BottomNav() {
  let isAdmin = false;
  try {
    const token = localStorage.getItem('token');
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]));
      isAdmin = payload.perfil === 'ADMIN';
    }
  } catch (e) {
    console.error('Erro ao ler token no BottomNav', e);
  }

  const links = [
    { to: '/', icon: 'home', label: 'Home' },
    { to: '/ranking', icon: 'social_leaderboard', label: 'Ranking' },
    { to: '/financeiro', icon: 'payments', label: 'Finanças' },
    { to: '/votos', icon: 'how_to_vote', label: 'Votos' },
    { to: '/perfil', icon: 'person', label: 'Perfil' },
  ];

  if (isAdmin) {
    links.push({ to: '/admin', icon: 'settings_suggest', label: 'Admin' });
  }

  return (
    <nav className="fixed bottom-6 left-4 right-4 md:left-1/2 md:-translate-x-1/2 max-w-[500px] z-50 rounded-3xl md:rounded-full bg-surface/90 glass-panel shadow-bento border border-outline/20">
      <div className="flex justify-around items-center w-full px-2 py-3">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            aria-label={label}
            className={({ isActive }) => cn(
              "relative flex flex-col items-center justify-center rounded-full px-2 py-1 transition-colors active:scale-90 duration-150 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary",
              isActive ? "bg-primary-container text-on-primary-container px-4" : "text-on-surface-variant hover:bg-surface-variant/50"
            )}
          >
            {({ isActive }) => (
              <>
                <span className={cn("material-symbols-outlined", isActive && "icon-fill")} aria-hidden="true">{icon}</span>
                <span className="font-label-bold text-label-bold mt-1 text-[10px] min-[360px]:text-[12px] sr-only min-[360px]:not-sr-only" aria-hidden="true">{label}</span>
                <span className={cn("absolute -bottom-1 h-1 w-1 rounded-full transition-all duration-300", isActive ? "bg-primary scale-100" : "bg-transparent scale-0")} aria-hidden="true"></span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
