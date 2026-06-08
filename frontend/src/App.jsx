import { BrowserRouter, Routes, Route, Outlet, Navigate, Link } from 'react-router-dom';
import { BottomNav } from './components/layout/BottomNav';
import { ToastContainer } from './components/ui/Toast';

import React, { Suspense } from 'react';

// Impacto: Uso de React.lazy permite o Code Splitting pelo Vite.
// Isso reduz o Initial Bundle Size (o bundle inicial carrega apenas o App e o layout),
// e diminui o Time To Interactive (TTI), carregando as páginas apenas sob demanda.
const LoginPage = React.lazy(() => import('./features/auth/LoginPage').then(module => ({ default: module.LoginPage })));
const HomePage = React.lazy(() => import('./features/home/HomePage').then(module => ({ default: module.HomePage })));
const AdminPage = React.lazy(() => import('./features/admin/AdminPage').then(module => ({ default: module.AdminPage })));
const VotosPage = React.lazy(() => import('./features/votos/VotosPage').then(module => ({ default: module.VotosPage })));
const AvaliacaoGaleraPage = React.lazy(() => import('./features/votos/AvaliacaoGaleraPage').then(module => ({ default: module.AvaliacaoGaleraPage })));
const RankingPage = React.lazy(() => import('./features/ranking/RankingPage').then(module => ({ default: module.RankingPage })));
const FinanceiroPage = React.lazy(() => import('./features/financeiro/FinanceiroPage').then(module => ({ default: module.FinanceiroPage })));
const PerfilPage = React.lazy(() => import('./features/perfil/PerfilPage').then(module => ({ default: module.PerfilPage })));

import { ForceVoteGuard } from './hooks/useForceVote';

function ProtectedRoute() {
  const token = localStorage.getItem('token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
}

function MainLayout() {
  return (
    <>
      <header className="fixed top-4 left-4 right-4 md:left-1/2 md:-translate-x-1/2 max-w-screen-xl z-50 bg-surface/90 glass-panel shadow-bento border border-outline/20 rounded-3xl md:rounded-full">
        <div className="flex items-center justify-between px-6 h-16 w-full">
          <div className="flex items-center gap-3">
            <img src="/assets/logo_peladafc.png" alt="Pelada FC Logo" className="w-10 h-10 object-contain drop-shadow-sm" />
            <h1 className="font-headline-sm text-primary font-bold tracking-tight">Pelada FC</h1>
          </div>
          <Link 
            to="/ranking"
            aria-label="Ver Ranking"
            className="w-10 h-10 flex items-center justify-center rounded-full bg-surface-variant hover:bg-surface-variant/80 transition-colors text-on-surface-variant active:scale-95 duration-100"
          >
            <span className="material-symbols-outlined">military_tech</span>
          </Link>
        </div>
      </header>
      
      <main className="w-full max-w-screen-xl mx-auto px-container-margin-mobile md:px-container-margin-desktop pt-28 pb-24 md:pb-0 min-h-screen">
        <ForceVoteGuard>
          <Outlet />
        </ForceVoteGuard>
      </main>
      
      <BottomNav />
    </>
  );
}

export default function App() {
  return (
    <>
      <ToastContainer />
      <BrowserRouter>
        <Suspense fallback={<div className="flex items-center justify-center min-h-screen text-on-surface-variant font-body-md">Carregando...</div>}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/admin" element={<AdminPage />} />
                <Route path="/votos" element={<VotosPage />} />
                <Route path="/avaliacao-galera" element={<AvaliacaoGaleraPage />} />
                <Route path="/ranking" element={<RankingPage />} />
                <Route path="/financeiro" element={<FinanceiroPage />} />
                <Route path="/perfil" element={<PerfilPage />} />
              </Route>
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </>
  );
}
