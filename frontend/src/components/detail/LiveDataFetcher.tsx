import { useState, useEffect, useCallback } from 'react';
import { getIntraday } from '../../api/marketData';

interface LiveDataFetcherProps {
  symbol: string;
}

export default function LiveDataFetcher({ symbol }: LiveDataFetcherProps) {
  const [interval, setInterval_] = useState(1);
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getIntraday(symbol, interval);
      if (result.data && result.data.length > 0) {
        setData(result.data);
        setError(null);
      } else {
        setData(null);
        setError(result.error || 'No data available');
      }
    } catch {
      setError('Failed to fetch live data');
    }
    setLoading(false);
  }, [symbol, interval]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const latestCandle = data?.[0] as { close?: number; high?: number; low?: number; volume?: number; datetime?: string } | undefined;

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Live Data - {symbol}</h3>
        <div className="flex items-center gap-2">
          <select
            value={interval}
            onChange={(e) => setInterval_(Number(e.target.value))}
            className="rounded border px-2 py-1 text-sm"
          >
            <option value={1}>1 Minute</option>
            <option value={30}>30 Minutes</option>
          </select>
          <button onClick={fetchData} disabled={loading} className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {latestCandle && (
        <div className="mt-3 grid grid-cols-4 gap-3 text-sm">
          <div className="rounded bg-gray-50 p-2">
            <p className="text-xs text-gray-500">Last Price</p>
            <p className="text-lg font-bold">{Number(latestCandle.close).toFixed(2)}</p>
          </div>
          <div className="rounded bg-gray-50 p-2">
            <p className="text-xs text-gray-500">High</p>
            <p className="font-semibold text-green-600">{Number(latestCandle.high).toFixed(2)}</p>
          </div>
          <div className="rounded bg-gray-50 p-2">
            <p className="text-xs text-gray-500">Low</p>
            <p className="font-semibold text-red-600">{Number(latestCandle.low).toFixed(2)}</p>
          </div>
          <div className="rounded bg-gray-50 p-2">
            <p className="text-xs text-gray-500">Volume</p>
            <p className="font-semibold">{Number(latestCandle.volume).toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
}
