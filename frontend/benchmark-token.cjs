const { performance } = require('perf_hooks');

const token = "header." + Buffer.from(JSON.stringify({ sub: "123", exp: Date.now() + 10000 })).toString('base64') + ".signature";
// Simulate localStorage
const localStorage = { getItem: () => token };

function original() {
  const token = localStorage.getItem('token');
  let currentUserId = null;
  if (token) {
    try {
      const payloadBase64 = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      currentUserId = parseInt(decodedPayload.sub);
    } catch (e) {
      console.error(e);
    }
  }
  return currentUserId;
}

// Emulate atob for Node.js
global.atob = (str) => Buffer.from(str, 'base64').toString('binary');

const ITERATIONS = 10000;

console.log("Measuring original implementation (simulating " + ITERATIONS + " renders)...");
let start = performance.now();
for (let i = 0; i < ITERATIONS; i++) {
  original();
}
let end = performance.now();
const originalTime = end - start;
console.log(`Original Time: ${originalTime.toFixed(2)} ms`);

// Cached implementation
let cachedUserId = null;
let initialized = false;

function optimized() {
  if (!initialized) {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payloadBase64 = token.split('.')[1];
        const decodedPayload = JSON.parse(atob(payloadBase64));
        cachedUserId = parseInt(decodedPayload.sub);
      } catch (e) {
        console.error(e);
      }
    }
    initialized = true;
  }
  return cachedUserId;
}

console.log("Measuring optimized implementation (simulating " + ITERATIONS + " renders)...");
start = performance.now();
for (let i = 0; i < ITERATIONS; i++) {
  optimized();
}
end = performance.now();
const optimizedTime = end - start;
console.log(`Optimized Time: ${optimizedTime.toFixed(2)} ms`);
console.log(`Improvement: ${((originalTime - optimizedTime) / originalTime * 100).toFixed(2)}%`);
