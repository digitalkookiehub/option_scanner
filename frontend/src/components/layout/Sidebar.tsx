import { useScreeningStore } from '../../store/screeningStore';

export default function Sidebar() {
  const {
    useMock, useLiveData, intradayInterval, loading,
    setUseMock, setUseLiveData, setIntradayInterval, runScreening,
    bullish, bearish, neutral, timestamp,
  } = useScreeningStore();

  return (
    <aside className="w-64 shrink-0 space-y-4 border-r bg-white p-4">
      <div>
        <h3 className="mb-2 font-semibold text-gray-800">Data Source</h3>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={useMock} onChange={(e) => setUseMock(e.target.checked)} />
          Use Mock Data
        </label>
        <label className="mt-1 flex items-center gap-2 text-sm">
          <input type="checkbox" checked={useLiveData} onChange={(e) => setUseLiveData(e.target.checked)} />
          Live Intraday Data
        </label>
      </div>

      <div>
        <h3 className="mb-2 font-semibold text-gray-800">Intraday Interval</h3>
        <select
          value={intradayInterval}
          onChange={(e) => setIntradayInterval(Number(e.target.value))}
          className="w-full rounded border px-2 py-1 text-sm"
        >
          <option value={1}>1 Minute</option>
          <option value={30}>30 Minutes</option>
        </select>
      </div>

      <button
        onClick={runScreening}
        disabled={loading}
        className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Screening...' : 'Run Screening'}
      </button>

      <div className="space-y-1 border-t pt-3 text-sm">
        <h3 className="font-semibold text-gray-800">Results</h3>
        <p className="text-green-600">Bullish: {bullish.length}</p>
        <p className="text-red-600">Bearish: {bearish.length}</p>
        <p className="text-gray-500">Neutral: {neutral.length}</p>
        {timestamp && <p className="mt-1 text-xs text-gray-400">Last: {timestamp}</p>}
      </div>
    </aside>
  );
}
