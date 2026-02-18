import { create } from 'zustand';
import type { ScreeningResult } from '../types/stock';
import type { OptionContract, TradeResult } from '../types/options';
import * as screeningApi from '../api/screening';
import * as optionsApi from '../api/options';

interface DetailState {
  selectedStock: ScreeningResult | null;
  optionChain: OptionContract[];
  spotPrice: number | null;
  expiries: string[];
  selectedExpiry: string;
  tradeResults: TradeResult[];
  loading: boolean;
  error: string | null;
  selectStock: (stock: ScreeningResult) => void;
  fetchStockDetail: (symbol: string, useMock?: boolean) => Promise<void>;
  fetchOptionChain: (symbol: string, expiryDate: string) => Promise<void>;
  fetchExpiries: (symbol: string) => Promise<void>;
  setSelectedExpiry: (expiry: string) => void;
  setTradeResults: (results: TradeResult[]) => void;
  clear: () => void;
}

export const useDetailStore = create<DetailState>((set) => ({
  selectedStock: null,
  optionChain: [],
  spotPrice: null,
  expiries: [],
  selectedExpiry: '',
  tradeResults: [],
  loading: false,
  error: null,

  selectStock: (stock) => set({ selectedStock: stock }),

  fetchStockDetail: async (symbol, useMock = true) => {
    set({ loading: true, error: null });
    try {
      const data = await screeningApi.screenSingleStock(symbol, useMock);
      if ('error' in data && !('trend' in data)) {
        set({ loading: false, error: (data as { error: string }).error });
      } else {
        set({ selectedStock: data as ScreeningResult, loading: false });
      }
    } catch {
      set({ loading: false, error: 'Failed to fetch stock detail' });
    }
  },

  fetchOptionChain: async (symbol, expiryDate) => {
    set({ loading: true, error: null });
    try {
      const data = await optionsApi.getOptionChain(symbol, expiryDate);
      set({
        optionChain: data.chain || [],
        spotPrice: data.spot_price || null,
        loading: false,
        error: data.error || null,
      });
    } catch {
      set({ loading: false, error: 'Failed to fetch option chain' });
    }
  },

  fetchExpiries: async (symbol) => {
    try {
      const data = await optionsApi.getExpiries(symbol);
      const expiries = data.expiries || [];
      set({ expiries, selectedExpiry: expiries[0] || '' });
    } catch {
      // ignore
    }
  },

  setSelectedExpiry: (expiry) => set({ selectedExpiry: expiry }),
  setTradeResults: (results) => set({ tradeResults: results }),
  clear: () => set({ selectedStock: null, optionChain: [], spotPrice: null, expiries: [], selectedExpiry: '', tradeResults: [] }),
}));
