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
    <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-[9999] animate-bounce-in max-w-sm w-[90%] md:w-auto">
      <div className={`px-5 py-3.5 rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.6)] text-[14px] flex items-center gap-3 border backdrop-blur-xl transition-all duration-300 ${
        isError 
          ? 'bg-[#111111]/95 text-white border-error/30 shadow-[0_0_20px_rgba(239,68,68,0.2)]' 
          : 'bg-[#111111]/95 text-white border-primary/40 shadow-[0_0_20px_rgba(234,179,8,0.15)]'
      }`}>
        {isError ? (
          <span className="material-symbols-outlined text-[22px] text-error" style={{ fontVariationSettings: "'FILL' 1" }}>error</span>
        ) : (
          <div className="flex items-center justify-center text-primary drop-shadow-[0_0_8px_rgba(234,179,8,0.6)]">
            <span className="material-symbols-outlined text-[22px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
          </div>
        )}
        <span className="font-semibold tracking-wide">{toast.message}</span>
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
