import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Card } from '../../components/ui/Card';
import api from '../../services/api';

export function LoginPage() {
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const telefoneLimpo = telefone.replace(/\D/g, '');
      const response = await api.post('/auth/login', { telefone: telefoneLimpo, senha });
      localStorage.setItem('token', response.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao realizar login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-background">
      <div className="w-full max-w-sm flex flex-col gap-8">
        <div className="text-center space-y-2">
          <h1 className="text-display-lg text-primary">Pelada FC</h1>
          <p className="text-body-md text-tertiary">Gerencie seu futebol com classe.</p>
        </div>

        <Card className="p-6">
          <form onSubmit={handleLogin} className="flex flex-col gap-6">
            <Input 
              label="Telefone" 
              placeholder="(11) 99999-9999" 
              value={telefone}
              onChange={(e) => setTelefone(e.target.value)}
              required
            />
            
            <Input 
              label="Senha" 
              type="password"
              placeholder="••••••••" 
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              error={error}
              autoComplete="current-password"
              required
            />

            <Button type="submit" disabled={loading} className="mt-2">
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
