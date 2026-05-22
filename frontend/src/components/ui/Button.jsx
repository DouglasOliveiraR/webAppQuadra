import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function Button({ 
  children, 
  variant = 'primary', 
  className, 
  ...props 
}) {
  const baseStyles = "w-full py-3 px-4 rounded-standard font-display font-bold text-base transition-all active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-primary text-on-primary hover:bg-primary/90 shadow-lvl1 hover:shadow-lvl2 hover:-translate-y-0.5",
    secondary: "border-2 border-primary text-primary hover:bg-primary/5",
    ghost: "text-primary hover:bg-primary/10",
  };

  return (
    <button 
      className={cn(baseStyles, variants[variant], className)}
      {...props}
    >
      {children}
    </button>
  );
}
