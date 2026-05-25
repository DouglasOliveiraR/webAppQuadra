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
    <nav className="fixed bottom-0 w-full z-50 rounded-t-xl bg-surface dark:bg-surface-dim shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
      <div className="flex justify-around items-center w-full max-w-screen-xl mx-auto px-2 py-3 pb-safe">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            aria-label={label}
            className={({ isActive }) => cn(
              "flex flex-col items-center justify-center rounded-full px-2 py-1 transition-colors active:scale-90 duration-150 ease-in-out",
              isActive ? "bg-primary-container text-on-primary-container px-4" : "text-on-surface-variant hover:bg-surface-variant/50"
            )}
          >
            {({ isActive }) => (
              <>
                <span className={cn("material-symbols-outlined", isActive && "icon-fill")}>{icon}</span>
                <span className="font-label-bold text-label-bold mt-1 text-[10px] min-[360px]:text-[12px]">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
