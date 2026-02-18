import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import ScreeningPage from './pages/ScreeningPage';
import AuthPage from './pages/AuthPage';
import DetailPage from './pages/DetailPage';

export default function App() {
  const fetchStatus = useAuthStore((s) => s.fetchStatus);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ScreeningPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/detail/:symbol" element={<DetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
