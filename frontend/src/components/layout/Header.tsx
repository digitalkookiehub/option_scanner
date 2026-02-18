import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useMarketHours } from '../../hooks/useMarketHours';

export default function Header() {
  const location = useLocation();
  const { status } = useAuthStore();
  const isMarketOpen = useMarketHours();

  return (
    <header className="border-b bg-white shadow-sm">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-bold text-gray-900">NSE Stock Screener</h1>
          <nav className="flex gap-1">
            <Link
              to="/"
              className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                location.pathname === '/' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Screener
            </Link>
            <Link
              to="/auth"
              className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                location.pathname === '/auth' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Auth
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${isMarketOpen ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
            {isMarketOpen ? 'Market Open' : 'Market Closed'}
          </span>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${status?.authenticated ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
            {status?.authenticated ? 'Connected' : 'Not Connected'}
          </span>
        </div>
      </div>
    </header>
  );
}
