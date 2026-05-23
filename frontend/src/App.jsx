import { BrowserRouter, Routes, Route, Outlet, Navigate } from 'react-router-dom';
import { BottomNav } from './components/layout/BottomNav';
import { ToastContainer } from './components/ui/Toast';

import { LoginPage } from './features/auth/LoginPage';
import { HomePage } from './features/home/HomePage';
import { AdminPage } from './features/admin/AdminPage';
import { VotosPage } from './features/votos/VotosPage';
import { RankingPage } from './features/ranking/RankingPage';
import { FinanceiroPage } from './features/financeiro/FinanceiroPage';
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
      <header className="fixed top-0 w-full z-50 shadow-sm bg-surface dark:bg-surface-dim">
        <div className="flex items-center justify-between px-container-margin-mobile md:px-container-margin-desktop h-16 w-full max-w-screen-xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-label-bold text-label-bold">
              PFC
            </div>
            <h1 className="font-headline-md text-headline-md text-primary font-bold">Pelada FC</h1>
          </div>
          <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors text-on-surface-variant dark:text-on-surface-variant active:scale-95 duration-100">
            <span className="material-symbols-outlined">military_tech</span>
          </button>
        </div>
      </header>
      
      <main className="w-full max-w-screen-xl mx-auto px-container-margin-mobile md:px-container-margin-desktop pt-20 pb-24 md:pb-0 min-h-screen">
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
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/admin" element={<AdminPage />} />
              <Route path="/votos" element={<VotosPage />} />
              <Route path="/ranking" element={<RankingPage />} />
              <Route path="/financeiro" element={<FinanceiroPage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}
