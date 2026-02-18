import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDetailStore } from '../store/detailStore';
import { useScreeningStore } from '../store/screeningStore';
import PageLayout from '../components/layout/PageLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import MacdHistogramAnalysis from '../components/detail/MacdHistogramAnalysis';
import MacdDiffTable from '../components/detail/MacdDiffTable';
import IchimokuMacdChart from '../components/detail/IchimokuMacdChart';
import LiveDataFetcher from '../components/detail/LiveDataFetcher';
import OptionChainViewer from '../components/detail/OptionChainViewer';
import OrderBook from '../components/trading/OrderBook';
import Positions from '../components/trading/Positions';

export default function DetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const { selectedStock, loading, error, fetchStockDetail, selectStock, clear } = useDetailStore();
  const { useMock, bullish, bearish, neutral } = useScreeningStore();

  useEffect(() => {
    if (!symbol) return;

    // Try to find in cached screening results first
    const allStocks = [...bullish, ...bearish, ...neutral];
    const cached = allStocks.find((s) => s.symbol === symbol);
    if (cached) {
      selectStock(cached);
    } else {
      fetchStockDetail(symbol, useMock);
    }

    return () => clear();
  }, [symbol, useMock, bullish, bearish, neutral, selectStock, fetchStockDetail, clear]);

  if (loading) return <PageLayout><LoadingSpinner text={`Loading ${symbol}...`} /></PageLayout>;
  if (error) return <PageLayout><div className="p-6"><ErrorAlert message={error} /></div></PageLayout>;
  if (!selectedStock) return <PageLayout><div className="p-6"><ErrorAlert message="Stock not found" /></div></PageLayout>;

  const stock = selectedStock;
  const trendColor = stock.trend === 'Bullish' ? 'text-green-600' : stock.trend === 'Bearish' ? 'text-red-600' : 'text-gray-600';

  return (
    <PageLayout>
      <div className="flex-1 space-y-4 overflow-y-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <button onClick={() => navigate('/')} className="text-sm text-blue-600 hover:underline">&larr; Back</button>
              <h2 className="text-2xl font-bold">{stock.symbol}</h2>
              <span className={`rounded px-2 py-1 text-sm font-semibold ${trendColor} ${stock.color === 'green' ? 'bg-green-100' : stock.color === 'red' ? 'bg-red-100' : 'bg-gray-100'}`}>
                {stock.trend}
              </span>
            </div>
            <p className="text-sm text-gray-500">{stock.name}</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{stock.current_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</p>
            <p className="text-sm text-gray-500">
              H: {stock.high_price.toFixed(2)} | L: {stock.low_price.toFixed(2)} | Span B: {stock.senkou_span_b.toFixed(2)}
            </p>
          </div>
        </div>

        {/* MACD Analysis */}
        <MacdHistogramAnalysis stock={stock} />

        {/* MACD Diff Table */}
        <MacdDiffTable values={stock.macd_hist_values} />

        {/* Ichimoku + MACD Chart */}
        {stock.indicators && stock.indicators.length > 0 && (
          <div className="rounded-lg border bg-white p-4">
            <h3 className="mb-3 text-lg font-semibold">Ichimoku Cloud + MACD Chart</h3>
            <IchimokuMacdChart indicators={stock.indicators as import('../types/stock').IndicatorData[]} />
          </div>
        )}

        {/* Live Data */}
        <LiveDataFetcher symbol={stock.symbol} />

        {/* Option Chain */}
        <OptionChainViewer symbol={stock.symbol} />

        {/* Order Book & Positions */}
        <div className="grid grid-cols-2 gap-4">
          <OrderBook />
          <Positions />
        </div>
      </div>
    </PageLayout>
  );
}
