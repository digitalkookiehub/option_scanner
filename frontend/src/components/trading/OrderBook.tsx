import { useState, useEffect } from 'react';
import { getOrderBook } from '../../api/orders';

export default function OrderBook() {
  const [orders, setOrders] = useState<Record<string, unknown>[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await getOrderBook();
      setOrders(data.orders || []);
      setError(data.error || null);
    } catch {
      setError('Failed to fetch order book');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Order Book</h3>
        <button onClick={fetchOrders} disabled={loading} className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
          Refresh
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {orders.length === 0 ? (
        <p className="mt-4 text-center text-sm text-gray-400">No orders today</p>
      ) : (
        <div className="mt-3 max-h-64 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr className="text-left text-gray-500">
                <th className="py-2">Symbol</th>
                <th>Type</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o, i) => (
                <tr key={i} className="border-t">
                  <td className="py-1.5 font-medium">{String(o.trading_symbol || o.instrument_token || '-')}</td>
                  <td className={String(o.transaction_type) === 'BUY' ? 'text-green-600' : 'text-red-600'}>{String(o.transaction_type || '-')}</td>
                  <td>{String(o.quantity || '-')}</td>
                  <td>{String(o.price || o.average_price || '-')}</td>
                  <td>{String(o.status || '-')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
