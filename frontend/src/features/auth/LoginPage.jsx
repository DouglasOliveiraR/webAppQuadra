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
    <div className="w-full min-h-screen bg-background text-on-background flex flex-col justify-center items-center relative overflow-hidden">
      {/* Decorative subtle background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-primary/20 rounded-full mix-blend-screen filter blur-[100px]"></div>
        <div className="absolute bottom-10 -left-20 w-72 h-72 bg-tertiary/20 rounded-full mix-blend-screen filter blur-[80px]"></div>
      </div>
      
      <div className="w-full max-w-md px-container-margin-mobile relative z-10 flex flex-col justify-center items-center">
        <div className="flex flex-col items-center mb-10 w-full animate-fade-in-up">
          <img 
            src="/assets/logo_peladafc.png" 
            alt="Pelada FC Logo" 
            className="w-32 h-32 object-contain mb-4 drop-shadow-[0_0_15px_rgba(34,197,94,0.3)] animate-float"
          />
          <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-on-background mb-2 text-center">Pelada FC</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant text-center">Área Exclusiva para Jogadores</p>
        </div>
      
      <form onSubmit={handleLogin} className="relative z-10 w-full space-y-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        {error && (
          <div className="bg-error/10 border border-error text-error p-3 rounded-lg text-sm text-center">
            {error}
          </div>
        )}
        
        <div className="bento-card bg-surface border border-outline/10 flex items-center px-4 py-3 focus-within:ring-2 focus-within:ring-primary focus-within:border-primary transition-all duration-200 shadow-ambient-1">
          <span className="material-symbols-outlined text-primary mr-3" aria-hidden="true">phone_iphone</span>
          <label htmlFor="telefone" className="sr-only">Telefone</label>
          <input 
            id="telefone"
            type="tel"
            value={telefone}
            onChange={(e) => setTelefone(e.target.value)}
            className="bg-transparent border-none outline-none text-on-surface w-full font-body-md placeholder-on-surface-variant/50 focus:ring-0 p-0"
            placeholder="Telefone (ex: 11999999999)"
            autoComplete="username"
            disabled={loading}
            required
          />
        </div>
        
        <div className="bento-card bg-surface border border-outline/10 flex items-center px-4 py-3 focus-within:ring-2 focus-within:ring-primary focus-within:border-primary transition-all duration-200 shadow-ambient-1">
          <span className="material-symbols-outlined text-primary mr-3" aria-hidden="true">lock</span>
          <label htmlFor="senha" className="sr-only">Senha</label>
          <input 
            id="senha"
            type={showPassword ? "text" : "password"}
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            className="bg-transparent border-none outline-none text-on-surface w-full font-body-md placeholder-on-surface-variant/50 focus:ring-0 p-0"
            placeholder="Senha"
            autoComplete="current-password"
            disabled={loading}
            required
          />
          <button 
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-on-surface-variant hover:text-primary transition-colors ml-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-full p-1"
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
            className="w-full bg-primary hover:bg-primary/90 text-on-primary font-headline-md text-headline-md py-4 rounded-xl shadow-ambient-2 hover:shadow-ambient-3 transition-all duration-200 active:scale-95 flex items-center justify-center disabled:opacity-50 disabled:active:scale-100"
          >
            {loading ? (
              <div className="w-6 h-6 border-2 border-on-primary border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Entrar na Resenha'
            )}
          </button>
        </div>
        
        <div className="text-center mt-6">
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Problemas para acessar? Fale com o Administrador.
          </p>
        </div>
      </form>
      </div>
    </div>
  );
}
