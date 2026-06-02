import { useState, useEffect } from 'react';
import api from '../services/api';

// Essa chave pública deve ser a VAPID_PUBLIC_KEY gerada no backend
// Para este MVP, podemos colocar como variavel de ambiente do Vite ou injetar dinamicamente.
// Idealmente seria uma variavel de ambiente VITE_VAPID_PUBLIC_KEY
const PUBLIC_VAPID_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || '';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function usePushNotifications() {
  const [isSupported, setIsSupported] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const [permission, setPermission] = useState(Notification.permission);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      setIsSupported(true);
      checkSubscription();
    }
  }, []);

  const checkSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const sub = await registration.pushManager.getSubscription();
      setSubscription(sub);
    } catch (error) {
      console.error('Erro ao buscar inscrição de push:', error);
    }
  };

  const subscribeToPush = async () => {
    if (!PUBLIC_VAPID_KEY) {
      console.error("VITE_VAPID_PUBLIC_KEY não está configurada no .env do frontend");
      return false;
    }

    setLoading(true);
    try {
      const perm = await Notification.requestPermission();
      setPermission(perm);

      if (perm === 'granted') {
        const registration = await navigator.serviceWorker.ready;
        const sub = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(PUBLIC_VAPID_KEY)
        });

        setSubscription(sub);

        // Enviar para o backend
        await api.post('/notificacoes/subscribe', {
          subscription: sub.toJSON()
        });
        
        setLoading(false);
        return true;
      } else {
        console.warn('Permissão negada para notificações.');
      }
    } catch (error) {
      console.error('Erro ao assinar notificações:', error);
    }
    setLoading(false);
    return false;
  };

  return {
    isSupported,
    permission,
    subscription,
    loading,
    subscribeToPush
  };
}
