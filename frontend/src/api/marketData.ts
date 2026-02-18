import client from './client';

export const getHistorical = (symbol: string, days = 200) =>
  client.get(`/market/historical/${symbol}`, { params: { days } }).then(r => r.data);

export const getIntraday = (symbol: string, interval = 1) =>
  client.get(`/market/intraday/${symbol}`, { params: { interval } }).then(r => r.data);

export const getLtp = (instrumentKey: string) =>
  client.get(`/market/ltp/${encodeURIComponent(instrumentKey)}`).then(r => r.data);
