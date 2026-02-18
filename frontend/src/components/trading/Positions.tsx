import { useState, useEffect } from 'react';
import { getPositions } from '../../api/orders';

export default function Positions() {
  const [positions, setPositions] = useState<Record<string, unknown>[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchPositions = async () => {
    setLoading(true);
    try {
      const data = await getPositions();
      setPositions(data.positions || []);
      setError(data.error || null);
    } catch {
      setError('Failed to fetch positions');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPositions();
  }, []);

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Positions</h3>
        <button onClick={fetchPositions} disabled={loading} className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
          Refresh
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {positions.length === 0 ? (
        <p className="mt-4 text-center text-sm text-gray-400">No open positions</p>
      ) : (
        <div className="mt-3 max-h-64 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr className="text-left text-gray-500">
                <th className="py-2">Symbol</th>
                <th>Qty</th>
                <th>Avg Price</th>
                <th>LTP</th>
                <th>P&L</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p, i) => {
                const pnl = Number(p.pnl || p.unrealised || 0);
                return (
                  <tr key={i} className="border-t">
                    <td className="py-1.5 font-medium">{String(p.trading_symbol || p.instrument_token || '-')}</td>
                    <td>{String(p.quantity || p.day_buy_quantity || '-')}</td>
                    <td>{String(p.average_price || p.buy_price || '-')}</td>
                    <td>{String(p.last_price || '-')}</td>
                    <td className={pnl >= 0 ? 'text-green-600' : 'text-red-600'}>{pnl.toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
