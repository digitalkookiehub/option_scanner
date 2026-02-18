import { create } from 'zustand';
import type { ScreeningResult } from '../types/stock';
import * as screeningApi from '../api/screening';

interface ScreeningState {
  bullish: ScreeningResult[];
  bearish: ScreeningResult[];
  neutral: ScreeningResult[];
  total: number;
  timestamp: string;
  loading: boolean;
  error: string | null;
  useMock: boolean;
  useLiveData: boolean;
  intradayInterval: number;
  expandMode: 'none' | 'all' | 'bullish' | 'bearish';
  runScreening: () => Promise<void>;
  fetchCachedResults: () => Promise<void>;
  setUseMock: (v: boolean) => void;
  setUseLiveData: (v: boolean) => void;
  setIntradayInterval: (v: number) => void;
  setExpandMode: (mode: 'none' | 'all' | 'bullish' | 'bearish') => void;
}

export const useScreeningStore = create<ScreeningState>((set, get) => ({
  bullish: [],
  bearish: [],
  neutral: [],
  total: 0,
  timestamp: '',
  loading: false,
  error: null,
  useMock: true,
  useLiveData: false,
  intradayInterval: 1,
  expandMode: 'none',

  runScreening: async () => {
    const { useMock, useLiveData, intradayInterval } = get();
    set({ loading: true, error: null });
    try {
      const data = await screeningApi.runScreening(useMock, useLiveData, intradayInterval);
      set({
        bullish: data.bullish,
        bearish: data.bearish,
        neutral: data.neutral,
        total: data.total,
        timestamp: data.timestamp,
        loading: false,
      });
    } catch (e) {
      set({ loading: false, error: 'Screening failed' });
    }
  },

  fetchCachedResults: async () => {
    try {
      const data = await screeningApi.getResults();
      if (data.total > 0) {
        set({
          bullish: data.bullish,
          bearish: data.bearish,
          neutral: data.neutral,
          total: data.total,
          timestamp: data.timestamp,
        });
      }
    } catch {
      // ignore
    }
  },

  setUseMock: (v) => set({ useMock: v }),
  setUseLiveData: (v) => set({ useLiveData: v }),
  setIntradayInterval: (v) => set({ intradayInterval: v }),
  setExpandMode: (mode) => set({ expandMode: mode }),
}));
