import React, { useState, useEffect } from 'react';

/**
 * Componente contêiner de Toasts que escuta eventos globais de notificação.
 * Pode ser renderizado no topo da árvore de componentes (ex: no App.jsx).
 */
export function ToastContainer() {
  const [toast, setToast] = useState(null);

  useEffect(() => {
    let timer;
    const handleToast = (e) => {
      setToast(null); // Limpa toast anterior imediatamente se houver outro pendente
      // Aguarda um pequeno delay para resetar animação
      setTimeout(() => {
        setToast(e.detail);
      }, 50);

      if (timer) clearTimeout(timer);
      
      timer = setTimeout(() => {
        setToast(null);
      }, 3000);
    };

    window.addEventListener('toast', handleToast);
    return () => {
      window.removeEventListener('toast', handleToast);
      if (timer) clearTimeout(timer);
    };
  }, []);

  if (!toast) return null;

  const isError = toast.type === 'error';

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 animate-bounce-in max-w-sm w-[90%] md:w-auto">
      <div className={`px-4 py-3 rounded-card shadow-lvl3 text-sm font-bold flex items-center gap-2 border backdrop-blur-md transition-all duration-300 ${
        isError 
          ? 'bg-error-container/95 text-on-error-container border-error/30' 
          : 'bg-primary-container/95 text-on-primary-container border-primary/30'
      }`}>
        <span className="text-base">{isError ? '⚠️' : '✅'}</span>
        <span>{toast.message}</span>
      </div>
    </div>
  );
}

/**
 * Função utilitária para disparar notificações de qualquer parte do app
 * (seja dentro de componentes, hooks ou arquivos de serviço JS puros).
 */
export const showToast = (message, type = 'success') => {
  window.dispatchEvent(new CustomEvent('toast', { detail: { message, type } }));
};
