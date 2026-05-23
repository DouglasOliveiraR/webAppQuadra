import { useState } from 'react';
import api from '../services/api';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const login = async (telefone, senha) => {
    setLoading(true);
    setError('');
    try {
      const payload = {
        telefone: telefone.replace(/\D/g, ''),
        senha: senha
      };

      const response = await api.post('/auth/login', payload);
      
      localStorage.setItem('token', response.data.access_token);
      return true;
    } catch (err) {
      console.error("Login Error:", err.response || err);
      setError(err.response?.data?.detail || 'Erro ao fazer login. Verifique as credenciais.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { login, loading, error };
}
