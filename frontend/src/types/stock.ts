export interface Stock {
  symbol: string;
  name: string;
  isin: string;
  has_options: number;
}

export interface MacdHistValue {
  day: number;
  date: string;
  macd_hist: number;
  close: number;
}

export interface IndicatorData {
  date: string;
  close: number;
  open: number;
  high: number;
  low: number;
  macd: number | null;
  macd_signal: number | null;
  macd_hist: number | null;
  tenkan_sen: number | null;
  kijun_sen: number | null;
  senkou_span_a: number | null;
  senkou_span_b: number | null;
  chikou_span: number | null;
}

export interface ScreeningResult {
  symbol: string;
  name: string;
  current_price: number;
  high_price: number;
  low_price: number;
  senkou_span_b: number;
  macd_hist: number;
  prev_macd_hist: number;
  trend: 'Bullish' | 'Bearish' | 'Neutral/Mixed';
  color: 'green' | 'red' | 'gray';
  macd_diffs_5d: number[];
  macd_hist_values: MacdHistValue[];
  intraday_strength_pct: number;
  indicators: IndicatorData[];
  raw_data: Record<string, unknown>[];
  last_updated: string;
}

export interface ScreeningResponse {
  bullish: ScreeningResult[];
  bearish: ScreeningResult[];
  neutral: ScreeningResult[];
  total: number;
  timestamp: string;
}
