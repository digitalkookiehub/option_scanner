import { useState } from 'react';
import { useScreeningStore } from '../../store/screeningStore';
import { previewStrategy, executeStrategy } from '../../api/orders';
import type { TradeResult } from '../../types/options';
import type { ScreeningResult } from '../../types/stock';
import Modal from '../common/Modal';

interface BuyDialogProps {
  onClose: () => void;
}

export default function BuyDialog({ onClose }: BuyDialogProps) {
  const { bullish, bearish } = useScreeningStore();
  const [tradeOption, setTradeOption] = useState<'bullish' | 'bearish' | 'mixed'>('bullish');
  const [profitTarget, setProfitTarget] = useState(2.5);
  const [results, setResults] = useState<TradeResult[]>([]);
  const [loading, setLoading] = useState(false);

  const getStocksToTrade = (): ScreeningResult[] => {
    const sortedBullish = [...bullish].sort((a, b) => a.intraday_strength_pct - b.intraday_strength_pct);
    const sortedBearish = [...bearish].sort((a, b) => a.intraday_strength_pct - b.intraday_strength_pct);

    if (tradeOption === 'bullish') return sortedBullish.slice(0, 3);
    if (tradeOption === 'bearish') return sortedBearish.slice(0, 3);
    // mixed
    return sortedBullish.length >= 2
      ? [...sortedBullish.slice(0, 2), ...sortedBearish.slice(0, 1)]
      : [...sortedBullish, ...sortedBearish.slice(0, 3 - sortedBullish.length)];
  };

  const stocks = getStocksToTrade();

  const handlePreview = async () => {
    setLoading(true);
    try {
      const data = await previewStrategy(
        stocks.map((s) => ({ symbol: s.symbol, trend: s.trend, current_price: s.current_price })),
        profitTarget,
      );
      setResults(data.results);
    } catch {
      // ignore
    }
    setLoading(false);
  };

  const handleExecute = async () => {
    setLoading(true);
    try {
      const data = await executeStrategy(
        stocks.map((s) => ({ symbol: s.symbol, trend: s.trend, current_price: s.current_price })),
        profitTarget,
      );
      setResults(data.results);
    } catch {
      // ignore
    }
    setLoading(false);
  };

  return (
    <Modal open title="Option Trading - Buy Top 3 Stocks" onClose={onClose}>
      <div className="space-y-4">
        {/* Strategy info */}
        <div className="rounded bg-blue-50 p-3 text-sm">
          <p className="font-medium">Strategy Rules:</p>
          <ul className="mt-1 list-inside list-disc text-gray-600">
            <li>Execution at 3:05 PM (or manual trigger)</li>
            <li>Closest In-The-Money (ITM) option contract</li>
            <li>Buy at current market price</li>
            <li>Sell limit order at +{profitTarget}% profit</li>
          </ul>
        </div>

        {/* Trade option */}
        <div>
          <label className="block text-sm font-medium">Select stocks to trade:</label>
          <div className="mt-1 flex gap-2">
            {[
              { v: 'bullish' as const, label: 'Top 3 Bullish (CALL)' },
              { v: 'bearish' as const, label: 'Top 3 Bearish (PUT)' },
              { v: 'mixed' as const, label: 'Mixed (2B + 1B)' },
            ].map(({ v, label }) => (
              <button
                key={v}
                onClick={() => setTradeOption(v)}
                className={`rounded px-3 py-1 text-xs ${tradeOption === v ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Selected stocks */}
        <div className="space-y-2">
          {stocks.map((s, i) => (
            <div key={s.symbol} className={`rounded-lg p-3 ${s.trend === 'Bullish' ? 'bg-green-50' : 'bg-red-50'}`}>
              <p className="font-semibold">
                {i + 1}. {s.symbol} - {s.name}
              </p>
              <p className="text-sm">Price: {s.current_price.toFixed(2)} | Trend: {s.trend} | Option: {s.trend === 'Bullish' ? 'CE' : 'PE'}</p>
            </div>
          ))}
          {stocks.length === 0 && <p className="text-sm text-gray-500">No stocks available for selected option.</p>}
        </div>

        {/* Profit target */}
        <div>
          <label className="block text-sm font-medium">Profit Target (%): {profitTarget}</label>
          <input
            type="range"
            min={1}
            max={10}
            step={0.5}
            value={profitTarget}
            onChange={(e) => setProfitTarget(Number(e.target.value))}
            className="mt-1 w-full"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleExecute}
            disabled={loading || stocks.length === 0}
            className="rounded bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
          >
            Execute Trades
          </button>
          <button
            onClick={handlePreview}
            disabled={loading || stocks.length === 0}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Preview Only
          </button>
          <button onClick={onClose} className="rounded bg-gray-200 px-4 py-2 text-sm hover:bg-gray-300">
            Cancel
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-2 border-t pt-3">
            <h4 className="font-semibold">Trade Results:</h4>
            {results.map((r, i) => (
              <div key={i} className={`rounded p-3 text-sm ${r.status === 'success' ? 'bg-green-50' : 'bg-red-50'}`}>
                <p className="font-medium">{r.symbol} - {r.status}</p>
                {r.option_type && <p>Option: {r.option_type} | Strike: {r.strike_price}</p>}
                {r.option_ltp && <p>LTP: {r.option_ltp} | Buy: {r.buy_limit_price} | Sell Target: {r.sell_target_price}</p>}
                {r.error && <p className="text-red-600">{r.error}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
}
