import React from 'react';
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import { BottomNav } from './components/layout/BottomNav';

import { LoginPage } from './features/auth/LoginPage';
import { HomePage } from './features/home/HomePage';

// Placeholder Pages for routing
const CheckinPage = () => <div className="p-4">Check-in Page</div>;
const VotosPage = () => <div className="p-4">Votação Page</div>;

function MainLayout() {
  return (
    <div className="min-h-screen bg-background pb-20">
      <main className="max-w-md mx-auto h-full">
        <Outlet />
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
        
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/checkin" element={<CheckinPage />} />
          <Route path="/votos" element={<VotosPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
