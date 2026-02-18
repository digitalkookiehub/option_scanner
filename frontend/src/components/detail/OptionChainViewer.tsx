import { useEffect } from 'react';
import { useDetailStore } from '../../store/detailStore';
import type { OptionContract } from '../../types/options';

interface OptionChainViewerProps {
  symbol: string;
}

export default function OptionChainViewer({ symbol }: OptionChainViewerProps) {
  const { optionChain, spotPrice, expiries, selectedExpiry, error, loading, fetchExpiries, fetchOptionChain, setSelectedExpiry } =
    useDetailStore();

  useEffect(() => {
    fetchExpiries(symbol);
  }, [symbol, fetchExpiries]);

  useEffect(() => {
    if (selectedExpiry) {
      fetchOptionChain(symbol, selectedExpiry);
    }
  }, [symbol, selectedExpiry, fetchOptionChain]);

  const calls = optionChain.filter((o: OptionContract) => o.option_type === 'CE').sort((a, b) => a.strike_price - b.strike_price);
  const puts = optionChain.filter((o: OptionContract) => o.option_type === 'PE').sort((a, b) => a.strike_price - b.strike_price);

  // Merge by strike
  const strikes = [...new Set([...calls.map((c) => c.strike_price), ...puts.map((p) => p.strike_price)])].sort((a, b) => a - b);
  const callMap = Object.fromEntries(calls.map((c) => [c.strike_price, c]));
  const putMap = Object.fromEntries(puts.map((p) => [p.strike_price, p]));

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Option Chain - {symbol}</h3>
        <div className="flex items-center gap-2 text-sm">
          {spotPrice && <span className="font-medium">Spot: {spotPrice.toFixed(2)}</span>}
          <select
            value={selectedExpiry}
            onChange={(e) => setSelectedExpiry(e.target.value)}
            className="rounded border px-2 py-1"
          >
            {expiries.map((exp) => (
              <option key={exp} value={exp}>{exp}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {loading && <p className="mt-2 text-sm text-gray-500">Loading option chain...</p>}

      {strikes.length > 0 && (
        <div className="mt-3 max-h-96 overflow-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-gray-100">
              <tr>
                <th colSpan={5} className="border-b py-1 text-center text-green-700">CALLS</th>
                <th className="border-b py-1 text-center font-bold">Strike</th>
                <th colSpan={5} className="border-b py-1 text-center text-red-700">PUTS</th>
              </tr>
              <tr className="text-gray-500">
                <th className="py-1 text-right">OI</th>
                <th className="text-right">Vol</th>
                <th className="text-right">IV</th>
                <th className="text-right">LTP</th>
                <th className="text-right">Delta</th>
                <th className="text-center font-bold">-</th>
                <th className="text-right">Delta</th>
                <th className="text-right">LTP</th>
                <th className="text-right">IV</th>
                <th className="text-right">Vol</th>
                <th className="text-right">OI</th>
              </tr>
            </thead>
            <tbody>
              {strikes.map((strike) => {
                const call = callMap[strike];
                const put = putMap[strike];
                const isATM = spotPrice && Math.abs(strike - spotPrice) === Math.min(...strikes.map((s) => Math.abs(s - spotPrice)));
                return (
                  <tr key={strike} className={isATM ? 'bg-yellow-50 font-medium' : 'hover:bg-gray-50'}>
                    <td className="py-0.5 text-right">{call?.oi?.toLocaleString() || '-'}</td>
                    <td className="text-right">{call?.volume?.toLocaleString() || '-'}</td>
                    <td className="text-right">{call?.iv ? (call.iv * 100).toFixed(1) + '%' : '-'}</td>
                    <td className="text-right font-mono">{call?.ltp?.toFixed(2) || '-'}</td>
                    <td className="text-right">{call?.delta?.toFixed(3) || '-'}</td>
                    <td className="text-center font-bold">{strike}</td>
                    <td className="text-right">{put?.delta?.toFixed(3) || '-'}</td>
                    <td className="text-right font-mono">{put?.ltp?.toFixed(2) || '-'}</td>
                    <td className="text-right">{put?.iv ? (put.iv * 100).toFixed(1) + '%' : '-'}</td>
                    <td className="text-right">{put?.volume?.toLocaleString() || '-'}</td>
                    <td className="text-right">{put?.oi?.toLocaleString() || '-'}</td>
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
