import axios from 'axios';

const getApiUrl = () => {
  const { protocol, hostname, port } = window.location;
  // Se rodando no servidor de desenvolvimento do Vite (porta 5173), direciona para a porta 8000
  if (port === '5173') {
    return `${protocol}//${hostname}:8000`;
  }
  // Em produção, Ngrok ou servido direto pelo FastAPI, usa o mesmo host/porta da página
  return `${protocol}//${hostname}${port ? `:${port}` : ''}`;
};

export const API_URL = getApiUrl();
export const API_PROTOCOL = window.location.protocol;

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
  },
});

// Interceptor para adicionar o token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor de resposta: ao receber 401 (token inválido ou sessão expirada),
// limpa o token e redireciona para a tela de login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Evita loop de redirecionamento se já estiver no /login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

