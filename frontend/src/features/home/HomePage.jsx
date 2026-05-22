import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

export function HomePage() {
  const [statusPresenca, setStatusPresenca] = useState('PENDENTE');

  const handlePresenca = (status) => {
    // Aqui no futuro faremos: api.put('/eventos/1/presencas/me', { status, ... })
    setStatusPresenca(status);
  };

  return (
    <div className="flex flex-col gap-6 p-4 pt-8">
      <header>
        <h2 className="text-headline-md text-tertiary">Próximo Jogo</h2>
        <h1 className="text-headline-lg-mobile text-on-background">Sexta, 01 Jun - 19:00</h1>
      </header>

      {/* Card de Churrasco Especial usando gradiente */}
      <Card variant="barbecue" className="p-5 flex items-center justify-between">
        <div>
          <h3 className="font-display font-bold text-lg drop-shadow-sm">Churrasco Confirmado 🔥</h3>
          <p className="text-white/80 text-sm font-medium">Valor: R$ 50,00</p>
        </div>
        <div className="bg-white/20 px-3 py-1 rounded-full border border-white/30 backdrop-blur-sm">
          <span className="text-sm font-bold">Eu vou!</span>
        </div>
      </Card>

      <section className="space-y-4 mt-4">
        <h3 className="text-label-bold text-tertiary uppercase">Sua Presença</h3>
        <Card className="p-4 flex gap-3">
          <Button 
            variant={statusPresenca === 'VOU' ? 'primary' : 'secondary'} 
            onClick={() => handlePresenca('VOU')}
          >
            Vou Jogar
          </Button>
          <Button 
            variant={statusPresenca === 'NAO_VOU' ? 'primary' : 'ghost'}
            className={statusPresenca === 'NAO_VOU' ? 'bg-error hover:bg-error/90 shadow-lvl1' : 'text-error hover:bg-error/10'}
            onClick={() => handlePresenca('NAO_VOU')}
          >
            Não Vou
          </Button>
        </Card>
      </section>
      
      <section className="space-y-4">
        <h3 className="text-label-bold text-tertiary uppercase mt-4">Confirmados (12)</h3>
        <div className="bg-white rounded-card shadow-sm border border-surface-variant overflow-hidden">
           {/* Mock list */}
           {[1,2,3].map(i => (
             <div key={i} className="px-4 py-3 border-b border-surface-variant last:border-0 flex items-center justify-between">
               <span className="font-semibold text-on-background">Douglas Oliveira</span>
               <span className="text-xs font-bold px-2 py-1 bg-surface-variant text-tertiary rounded-pill">LINHA</span>
             </div>
           ))}
        </div>
      </section>
    </div>
  );
}
