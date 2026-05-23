import React from 'react';
import { useFinanceiro } from '../../hooks/useFinanceiro';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Wallet, CheckCircle, Clock } from 'lucide-react';

export function FinanceiroPage() {
  const { pendencias, loading, actionLoading, error, baixarPagamento } = useFinanceiro();

  // Decodificando token para verificar perfil ADMIN (simples para o MVP)
  const token = localStorage.getItem('token');
  let isAdmin = false;
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      isAdmin = payload.perfil === 'ADMIN';
    } catch (e) {
      console.error("Erro ao ler token", e);
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full pt-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Estatísticas
  const totalPendente = pendencias.filter(p => p.status_pagamento === 'PENDENTE').reduce((acc, curr) => acc + curr.valor, 0);

  return (
    <div className="flex flex-col gap-6 p-4 pt-8 pb-32">
      <header className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
          <Wallet className="text-primary" size={24} />
        </div>
        <div>
          <h2 className="text-headline-md text-tertiary">Sua Carteira</h2>
          <h1 className="text-headline-lg-mobile text-on-background font-bold">Resumo Financeiro</h1>
        </div>
      </header>

      {/* Resumo Card */}
      <Card variant="filled" className="bg-gradient-to-br from-surface to-surface-variant border border-primary/20 p-6">
        <p className="text-sm text-on-background/70 mb-1">Total Pendente</p>
        <h2 className={`text-4xl font-black ${totalPendente > 0 ? 'text-error' : 'text-primary'}`}>
          R$ {totalPendente.toFixed(2).replace('.', ',')}
        </h2>
        {totalPendente === 0 && (
          <div className="mt-4 flex items-center gap-2 text-primary text-sm font-bold">
            <CheckCircle size={16} /> Tudo em dia! Você é um exemplo.
          </div>
        )}
      </Card>

      {error && <p className="text-error text-center">{error}</p>}

      {/* Lista de Transações */}
      <div className="flex flex-col gap-3 mt-4">
        <h3 className="font-bold text-on-background mb-2">Histórico de Cobranças</h3>
        
        {pendencias.length === 0 ? (
          <p className="text-center text-on-background/50">Nenhuma cobrança encontrada.</p>
        ) : (
          pendencias.map((item) => (
            <Card key={item.id} variant="elevated" className="flex items-center justify-between p-4 border-l-4" style={{ borderLeftColor: item.status_pagamento === 'PAGO' ? '#10B981' : '#EF4444' }}>
              <div className="flex flex-col">
                <span className="font-bold text-on-background capitalize">{item.tipo}</span>
                <span className="text-sm text-on-background/60 flex items-center gap-1 mt-1">
                  {item.status_pagamento === 'PAGO' ? <CheckCircle size={14} className="text-green-500" /> : <Clock size={14} className="text-error" />}
                  {item.status_pagamento}
                </span>
              </div>
              
              <div className="flex flex-col items-end gap-2">
                <span className="font-bold text-lg text-on-background">R$ {item.valor.toFixed(2).replace('.', ',')}</span>
                
                {item.status_pagamento === 'PENDENTE' && isAdmin && (
                  <Button 
                    variant="primary" 
                    size="sm"
                    className="text-xs px-2 py-1 h-auto"
                    disabled={actionLoading}
                    onClick={() => baixarPagamento(item.id)}
                  >
                    Dar Baixa
                  </Button>
                )}
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
