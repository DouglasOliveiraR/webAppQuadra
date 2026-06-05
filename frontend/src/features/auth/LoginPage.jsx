import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export function LoginPage() {
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const navigate = useNavigate();
  const { login, loading, error } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    const success = await login(telefone, senha);
    if (success) {
      navigate('/');
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#111827] text-white flex flex-col justify-center items-center relative overflow-hidden">
      {/* Decorative subtle background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-primary-container rounded-full mix-blend-screen filter blur-[100px] opacity-20"></div>
        <div className="absolute bottom-10 -left-20 w-72 h-72 bg-primary rounded-full mix-blend-screen filter blur-[80px] opacity-10"></div>
      </div>
      
      <div className="w-full max-w-md px-container-margin-mobile relative z-10 flex flex-col justify-center items-center">
        <div className="flex flex-col items-center mb-10 w-full">
        <div className="w-24 h-24 rounded-full bg-[#1f2937] flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(34,197,94,0.15)] border border-[#374151]">
          <span className="material-symbols-outlined text-[48px] text-[#22c55e]" style={{fontVariationSettings: "'FILL' 1"}}>
            sports_soccer
          </span>
        </div>
        <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-white mb-2 text-center">Pelada FC</h1>
        <p className="font-body-sm text-body-sm text-gray-400 text-center">Área Exclusiva para Jogadores</p>
      </div>
      
      <form onSubmit={handleLogin} className="relative z-10 w-full space-y-4">
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded-lg text-sm text-center">
            {error}
          </div>
        )}
        
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg flex items-center px-4 py-3 focus-within:ring-2 focus-within:ring-green-500/50 focus-within:border-green-500 transition-all duration-200">
          <span className="material-symbols-outlined text-gray-400 mr-3" aria-hidden="true">phone_iphone</span>
          <label htmlFor="telefone" className="sr-only">Telefone</label>
          <input 
            id="telefone"
            type="tel"
            value={telefone}
            onChange={(e) => setTelefone(e.target.value)}
            className="dark-autofill bg-transparent border-none outline-none text-white w-full font-body-md placeholder-gray-500 focus:ring-0 p-0"
            placeholder="Telefone (ex: 11999999999)"
            autoComplete="username"
            disabled={loading}
            required
          />
        </div>
        
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg flex items-center px-4 py-3 focus-within:ring-2 focus-within:ring-green-500/50 focus-within:border-green-500 transition-all duration-200">
          <span className="material-symbols-outlined text-gray-400 mr-3" aria-hidden="true">lock</span>
          <label htmlFor="senha" className="sr-only">Senha</label>
          <input 
            id="senha"
            type={showPassword ? "text" : "password"}
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            className="dark-autofill bg-transparent border-none outline-none text-white w-full font-body-md placeholder-gray-500 focus:ring-0 p-0"
            placeholder="Senha"
            autoComplete="current-password"
            disabled={loading}
            required
          />
          <button 
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-gray-400 hover:text-white transition-colors ml-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-full p-1"
            aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
          >
            <span className="material-symbols-outlined" aria-hidden="true">
              {showPassword ? 'visibility' : 'visibility_off'}
            </span>
          </button>
        </div>
        
        <div className="pt-4 pb-2">
          <button 
            type="submit"
            disabled={loading}
            className="w-full bg-[#22c55e] hover:bg-[#16a34a] text-[#004b1e] font-headline-md text-headline-md py-4 rounded-xl shadow-[0_4px_14px_0_rgba(34,197,94,0.39)] hover:shadow-[0_6px_20px_rgba(34,197,94,0.23)] transition-all duration-200 active:scale-95 flex items-center justify-center disabled:opacity-50 disabled:active:scale-100"
          >
            {loading ? (
              <div className="w-6 h-6 border-2 border-[#004b1e] border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Entrar na Resenha'
            )}
          </button>
        </div>
        
        <div className="text-center mt-6">
          <p className="font-body-sm text-body-sm text-gray-500">
            Problemas para acessar? Fale com o Administrador.
          </p>
        </div>
      </form>
      </div>
    </div>
  );
}
