import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import App from './App.jsx'

import { registerSW } from 'virtual:pwa-register'

// Registro automático do Service Worker gerado pelo Vite PWA
if ('serviceWorker' in navigator) {
  const updateSW = registerSW({
    onNeedRefresh() {
      if (confirm('Nova versão disponível. Deseja atualizar agora?')) {
        updateSW(true)
      }
    },
    onOfflineReady() {
      console.info('Aplicativo pronto para uso offline.')
    },
  })
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
