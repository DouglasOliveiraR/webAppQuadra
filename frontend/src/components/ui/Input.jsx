import React, { forwardRef } from 'react';
import { cn } from './Button';

export const Input = forwardRef(({ className, label, error, ...props }, ref) => {
  return (
    <div className="w-full flex flex-col gap-2">
      {label && <label className="text-label-bold text-on-background">{label}</label>}
      <input
        ref={ref}
        className={cn(
          "w-full px-4 py-3 bg-surface-variant rounded-standard text-body-md text-on-background placeholder:text-on-background/50 outline-none border border-transparent transition-all",
          "focus:border-primary focus:ring-2 focus:ring-primary/20",
          error && "border-error focus:border-error focus:ring-error/20",
          className
        )}
        {...props}
      />
      {error && <span className="text-body-sm text-error">{error}</span>}
    </div>
  );
});

Input.displayName = 'Input';
