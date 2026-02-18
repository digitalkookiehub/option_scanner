import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ScreeningResult } from '../../types/stock';

interface StockCardProps {
  stock: ScreeningResult;
  expanded: boolean;
}

export default function StockCard({ stock, expanded }: StockCardProps) {
  const [isExpanded, setIsExpanded] = useState(expanded);
  const navigate = useNavigate();

  const bgColor =
    stock.color === 'green' ? 'bg-green-50 border-green-200' :
    stock.color === 'red' ? 'bg-red-50 border-red-200' :
    'bg-gray-50 border-gray-200';

  const trendBadge =
    stock.trend === 'Bullish' ? 'bg-green-100 text-green-800' :
    stock.trend === 'Bearish' ? 'bg-red-100 text-red-800' :
    'bg-gray-100 text-gray-600';

  return (
    <div className={`mb-2 rounded-lg border ${bgColor} p-3`}>
      <div className="flex cursor-pointer items-center justify-between" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-900">{stock.symbol}</span>
            <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${trendBadge}`}>{stock.trend}</span>
            <span className="text-xs text-gray-500">{stock.intraday_strength_pct.toFixed(4)}%</span>
          </div>
          <p className="truncate text-xs text-gray-500">{stock.name}</p>
        </div>
        <div className="text-right">
          <p className="font-semibold">{stock.current_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</p>
          <p className={`text-xs ${stock.macd_hist > stock.prev_macd_hist ? 'text-green-600' : 'text-red-600'}`}>
            MACD: {stock.macd_hist.toFixed(4)}
          </p>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-3 border-t pt-3 text-xs">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-500">High:</span> {stock.high_price.toFixed(2)}
            </div>
            <div>
              <span className="text-gray-500">Low:</span> {stock.low_price.toFixed(2)}
            </div>
            <div>
              <span className="text-gray-500">Span B:</span> {stock.senkou_span_b.toFixed(2)}
            </div>
            <div>
              <span className="text-gray-500">Strength:</span> {stock.intraday_strength_pct.toFixed(4)}%
            </div>
          </div>

          <div className="mt-2">
            <p className="font-medium text-gray-700">MACD Hist 5-Day Diffs:</p>
            <div className="mt-1 flex gap-1">
              {stock.macd_diffs_5d.map((d, i) => (
                <span key={i} className={`rounded px-1.5 py-0.5 text-xs ${d > 0 ? 'bg-green-100 text-green-700' : d < 0 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'}`}>
                  {d > 0 ? '+' : ''}{d.toFixed(4)}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-2">
            <p className="font-medium text-gray-700">MACD Hist Values:</p>
            <table className="mt-1 w-full text-xs">
              <thead>
                <tr className="text-gray-500">
                  <th className="text-left">Date</th>
                  <th className="text-right">Hist</th>
                  <th className="text-right">Close</th>
                </tr>
              </thead>
              <tbody>
                {stock.macd_hist_values.map((v, i) => (
                  <tr key={i}>
                    <td>{typeof v.date === 'string' ? v.date : String(v.date)}</td>
                    <td className={`text-right ${v.macd_hist >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {v.macd_hist.toFixed(4)}
                    </td>
                    <td className="text-right">{v.close.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-3 flex gap-2">
            <button
              onClick={() => navigate(`/detail/${stock.symbol}`)}
              className="rounded bg-blue-600 px-3 py-1 text-xs text-white hover:bg-blue-700"
            >
              View Detail
            </button>
          </div>

          <p className="mt-2 text-gray-400">Updated: {stock.last_updated}</p>
        </div>
      )}
    </div>
  );
}
