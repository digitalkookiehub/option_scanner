import type { TradeResult } from '../../types/options';

export default function TradeResults({ results }: { results: TradeResult[] }) {
  if (results.length === 0) return null;

  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-3 text-lg font-semibold">Trade Results</h3>
      <div className="space-y-2">
        {results.map((r, i) => (
          <div key={i} className={`rounded-lg p-3 ${r.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{r.symbol}</span>
              <span className={`rounded px-2 py-0.5 text-xs font-medium ${r.status === 'success' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                {r.status}
              </span>
            </div>
            <div className="mt-1 grid grid-cols-2 gap-2 text-sm">
              {r.option_type && <p>Type: {r.option_type}</p>}
              {r.strike_price && <p>Strike: {r.strike_price}</p>}
              {r.option_ltp && <p>Option LTP: {r.option_ltp}</p>}
              {r.buy_limit_price && <p>Buy Price: {r.buy_limit_price}</p>}
              {r.sell_target_price && <p>Sell Target: {r.sell_target_price}</p>}
              {r.lot_size && <p>Lot Size: {r.lot_size}</p>}
            </div>
            {r.error && <p className="mt-1 text-sm text-red-600">{r.error}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
