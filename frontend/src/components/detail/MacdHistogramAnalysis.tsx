import type { ScreeningResult } from '../../types/stock';

export default function MacdHistogramAnalysis({ stock }: { stock: ScreeningResult }) {
  const histIncreasing = stock.macd_hist > stock.prev_macd_hist;

  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-3 text-lg font-semibold">MACD Histogram Analysis</h3>

      <div className="grid grid-cols-3 gap-4 text-sm">
        <div className="rounded bg-gray-50 p-3">
          <p className="text-gray-500">Current MACD Hist</p>
          <p className={`text-xl font-bold ${stock.macd_hist >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {stock.macd_hist.toFixed(4)}
          </p>
        </div>
        <div className="rounded bg-gray-50 p-3">
          <p className="text-gray-500">Previous MACD Hist</p>
          <p className="text-xl font-bold text-gray-800">{stock.prev_macd_hist.toFixed(4)}</p>
        </div>
        <div className="rounded bg-gray-50 p-3">
          <p className="text-gray-500">Trend</p>
          <p className={`text-xl font-bold ${histIncreasing ? 'text-green-600' : 'text-red-600'}`}>
            {histIncreasing ? 'Increasing' : 'Decreasing'}
          </p>
        </div>
      </div>

      <div className="mt-4">
        <p className="font-medium">5-Day MACD Histogram Differences:</p>
        <div className="mt-2 flex gap-2">
          {stock.macd_diffs_5d.map((d, i) => (
            <div key={i} className={`flex-1 rounded p-2 text-center ${d > 0 ? 'bg-green-100' : d < 0 ? 'bg-red-100' : 'bg-gray-100'}`}>
              <p className="text-xs text-gray-500">Day {i + 1}</p>
              <p className={`font-mono text-sm font-bold ${d > 0 ? 'text-green-700' : d < 0 ? 'text-red-700' : 'text-gray-500'}`}>
                {d > 0 ? '+' : ''}{d.toFixed(4)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
