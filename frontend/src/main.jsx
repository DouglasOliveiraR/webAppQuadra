import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import App from './App.jsx'

// Registro do Service Worker para suporte a PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(reg => {
        if (import.meta.env.DEV) {
          console.info('Service Worker registrado com sucesso:', reg.scope);
        }
      })
      .catch(err => console.error('Falha ao registrar Service Worker:', err));
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
