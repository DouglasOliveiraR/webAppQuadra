const perfHooks = require('perf_hooks');
const performance = perfHooks.performance;

const numUsers = 10000;
const numPresencas = 10000;

const fixos = [];
for (let i = 0; i < numUsers; i++) {
  fixos.push({ id: i, nome: `User ${i}`, perfil: 'MENSALISTA' });
}

const presencas = [];
for (let i = 0; i < numPresencas; i++) {
  presencas.push({ usuario_id: i, posicao: 'Linha', vai_churrasco: true, checkin_validado: true });
}

function runOriginal() {
  const start = performance.now();
  const fixosMapped = fixos.map(u => {
    const p = presencas.find(pres => pres.usuario_id === u.id);
    return {
      usuario_id: u.id,
      posicao: p?.posicao || 'Linha',
      vai_churrasco: p?.vai_churrasco || false,
      checkin_validado: p?.checkin_validado || false
    };
  });
  const end = performance.now();
  return end - start;
}

function runOptimized() {
  const start = performance.now();
  const presencasMap = {};
  for (const pres of presencas) {
    presencasMap[pres.usuario_id] = pres;
  }

  const fixosMapped = fixos.map(u => {
    const p = presencasMap[u.id];
    return {
      usuario_id: u.id,
      posicao: p?.posicao || 'Linha',
      vai_churrasco: p?.vai_churrasco || false,
      checkin_validado: p?.checkin_validado || false
    };
  });
  const end = performance.now();
  return end - start;
}

const t1 = runOriginal();
const t2 = runOptimized();

console.log(`Original: ${t1.toFixed(2)} ms`);
console.log(`Optimized: ${t2.toFixed(2)} ms`);
console.log(`Improvement: ${(t1 / t2).toFixed(2)}x faster`);
