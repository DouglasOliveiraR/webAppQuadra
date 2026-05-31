const jogadoresConfirmados = Array.from({ length: 50 }, (_, i) => ({ usuario_id: i, usuario_nome: `Jogador ${i}` }));
const pendenciasAdmin = Array.from({ length: 1000 }, (_, i) => ({
  id: i,
  usuario_id: i % 100,
  tipo: i % 2 === 0 ? 'CHURRASCO_1' : 'MENSALIDADE',
  status_pagamento: i % 3 === 0 ? 'PAGO' : 'PENDENTE',
  valor: 40
}));
const eventoDoMes = { id: 1 };

function baseline() {
  let count = 0;
  jogadoresConfirmados.map((jogador) => {
    const tipoChurrasco = `CHURRASCO_${eventoDoMes?.id}`;
    const registroChurras = pendenciasAdmin.find(
      p => p.usuario_id === jogador.usuario_id && p.tipo === tipoChurrasco
    );
    if (registroChurras) count++;
  });
  return count;
}

function optimized() {
  let count = 0;
  const tipoChurrasco = `CHURRASCO_${eventoDoMes?.id}`;
  const map = new Map();
  for (let i = 0; i < pendenciasAdmin.length; i++) {
    const p = pendenciasAdmin[i];
    if (p.tipo === tipoChurrasco) {
      map.set(p.usuario_id, p);
    }
  }

  jogadoresConfirmados.map((jogador) => {
    const registroChurras = map.get(jogador.usuario_id);
    if (registroChurras) count++;
  });
  return count;
}

const ITERATIONS = 10000;

console.log("Benchmarking...");
let start = performance.now();
for (let i = 0; i < ITERATIONS; i++) baseline();
let end = performance.now();
console.log(`Baseline: ${(end - start).toFixed(2)} ms`);

start = performance.now();
for (let i = 0; i < ITERATIONS; i++) optimized();
end = performance.now();
console.log(`Optimized: ${(end - start).toFixed(2)} ms`);
