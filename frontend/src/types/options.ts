export interface OptionContract {
  strike_price: number;
  expiry: string | null;
  option_type: 'CE' | 'PE';
  oi: number;
  oi_change: number;
  volume: number;
  ltp: number;
  bid_price: number;
  ask_price: number;
  iv: number;
  delta: number;
  theta: number;
  gamma: number;
  vega: number;
  instrument_key: string;
}

export interface TradeResult {
  symbol: string;
  trend: string;
  current_price: number;
  status: string;
  option_type: string | null;
  strike_price: number | null;
  trading_symbol: string | null;
  lot_size: number | null;
  expiry_date: string | null;
  option_ltp: number | null;
  buy_limit_price: number | null;
  sell_target_price: number | null;
  buy_order_id: string | null;
  sell_order_id: string | null;
  error: string | null;
}
