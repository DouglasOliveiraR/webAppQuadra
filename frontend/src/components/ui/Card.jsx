import React from 'react';
import { cn } from './Button';

export function Card({ children, className, variant = 'default', ...props }) {
  const baseStyles = "w-full rounded-card overflow-hidden transition-all duration-200";
  
  const variants = {
    default: "bg-white shadow-lvl1 hover:shadow-lvl2 hover:-translate-y-0.5 border border-surface-variant",
    barbecue: "bg-gradient-to-br from-barbecue-start to-barbecue-end text-white shadow-lvl2 border border-white/20",
    glass: "glass-panel"
  };

  return (
    <div className={cn(baseStyles, variants[variant], className)} {...props}>
      {children}
    </div>
  );
}
