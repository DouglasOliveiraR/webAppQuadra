import { BrowserRouter, Routes, Route, Outlet, Navigate } from 'react-router-dom';
import { BottomNav } from './components/layout/BottomNav';

import { LoginPage } from './features/auth/LoginPage';
import { HomePage } from './features/home/HomePage';
import { CheckinPage } from './features/admin/CheckinPage';
import { VotosPage } from './features/votos/VotosPage';
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
    <div className="min-h-screen bg-background pb-20">
      <main className="max-w-md mx-auto h-full">
        <ForceVoteGuard>
          <Outlet />
        </ForceVoteGuard>
      </main>
      <BottomNav />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Rotas Protegidas */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/checkin" element={<CheckinPage />} />
            <Route path="/votos" element={<VotosPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
