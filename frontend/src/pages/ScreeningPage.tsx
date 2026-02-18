import { useEffect, useState, useCallback } from 'react';
import { useScreeningStore } from '../store/screeningStore';
import { useAutoRefresh } from '../hooks/useAutoRefresh';
import PageLayout from '../components/layout/PageLayout';
import Sidebar from '../components/layout/Sidebar';
import StockColumn from '../components/screening/StockColumn';
import ExpandCollapseBar from '../components/screening/ExpandCollapseBar';
import ScreeningProgress from '../components/screening/ScreeningProgress';
import BuyDialog from '../components/trading/BuyDialog';

export default function ScreeningPage() {
  const { bullish, bearish, neutral, loading, expandMode, fetchCachedResults, runScreening } = useScreeningStore();
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [showBuyDialog, setShowBuyDialog] = useState(false);

  useEffect(() => {
    fetchCachedResults();
  }, [fetchCachedResults]);

  const handleAutoRefresh = useCallback(() => {
    if (!loading) runScreening();
  }, [loading, runScreening]);

  useAutoRefresh(handleAutoRefresh, 60000, autoRefresh);

  const isBullishExpanded = expandMode === 'all' || expandMode === 'bullish';
  const isBearishExpanded = expandMode === 'all' || expandMode === 'bearish';
  const isNeutralExpanded = expandMode === 'all';

  return (
    <PageLayout>
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden p-4">
        {/* Top bar */}
        <div className="flex items-center justify-between">
          <ExpandCollapseBar />
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
              Auto-refresh (60s)
            </label>
            <button
              onClick={() => setShowBuyDialog(true)}
              disabled={bullish.length === 0 && bearish.length === 0}
              className="rounded-lg bg-orange-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-orange-700 disabled:opacity-50"
            >
              Buy Top 3
            </button>
          </div>
        </div>

        {/* Main content */}
        {loading ? (
          <ScreeningProgress />
        ) : (
          <div className="mt-3 grid flex-1 grid-cols-3 gap-4 overflow-hidden">
            <StockColumn title="Bullish" stocks={bullish} color="green" expanded={isBullishExpanded} />
            <StockColumn title="Bearish" stocks={bearish} color="red" expanded={isBearishExpanded} />
            <StockColumn title="Neutral/Mixed" stocks={neutral} color="gray" expanded={isNeutralExpanded} />
          </div>
        )}
      </div>

      {showBuyDialog && <BuyDialog onClose={() => setShowBuyDialog(false)} />}
    </PageLayout>
  );
}
