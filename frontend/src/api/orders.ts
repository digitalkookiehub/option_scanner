import client from './client';
import type { TradeResult } from '../types/options';

export const placeOrder = (data: {
  instrument_key: string;
  quantity: number;
  transaction_type: string;
  order_type?: string;
  price?: number;
  trigger_price?: number;
  product?: string;
}) => client.post('/orders/place', data).then(r => r.data);

export const getOrderBook = () =>
  client.get('/orders/book').then(r => r.data);

export const getPositions = () =>
  client.get('/orders/positions').then(r => r.data);

export const executeStrategy = (stocks: Record<string, unknown>[], profitTargetPct = 2.5) =>
  client.post<{ results: TradeResult[] }>('/orders/execute-strategy', {
    stocks,
    profit_target_pct: profitTargetPct,
  }).then(r => r.data);

export const previewStrategy = (stocks: Record<string, unknown>[], profitTargetPct = 2.5) =>
  client.post<{ results: TradeResult[]; preview: boolean }>('/orders/preview-strategy', {
    stocks,
    profit_target_pct: profitTargetPct,
  }).then(r => r.data);
