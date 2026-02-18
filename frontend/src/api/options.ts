import client from './client';

export const getOptionContracts = (symbol: string, expiryDate?: string) =>
  client.get(`/options/contracts/${symbol}`, { params: { expiry_date: expiryDate } }).then(r => r.data);

export const getOptionChain = (symbol: string, expiryDate: string) =>
  client.get(`/options/chain/${symbol}`, { params: { expiry_date: expiryDate } }).then(r => r.data);

export const getExpiries = (symbol: string) =>
  client.get(`/options/expiries/${symbol}`).then(r => r.data);

export const findItmOption = (symbol: string, currentPrice: number, optionType: string, expiryDate?: string) =>
  client.get(`/options/itm/${symbol}`, {
    params: { current_price: currentPrice, option_type: optionType, expiry_date: expiryDate },
  }).then(r => r.data);
