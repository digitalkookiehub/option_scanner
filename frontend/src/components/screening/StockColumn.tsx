import type { ScreeningResult } from '../../types/stock';
import StockCard from './StockCard';

interface StockColumnProps {
  title: string;
  stocks: ScreeningResult[];
  color: string;
  expanded: boolean;
}

export default function StockColumn({ title, stocks, color, expanded }: StockColumnProps) {
  const headerColor =
    color === 'green' ? 'bg-green-600' :
    color === 'red' ? 'bg-red-600' :
    'bg-gray-600';

  return (
    <div className="flex flex-col">
      <div className={`${headerColor} rounded-t-lg px-4 py-2 text-white`}>
        <h3 className="font-semibold">{title} ({stocks.length})</h3>
      </div>
      <div className="max-h-[calc(100vh-220px)] overflow-y-auto rounded-b-lg border bg-white p-2">
        {stocks.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-400">No stocks found</p>
        ) : (
          stocks.map((stock) => (
            <StockCard key={stock.symbol} stock={stock} expanded={expanded} />
          ))
        )}
      </div>
    </div>
  );
}
