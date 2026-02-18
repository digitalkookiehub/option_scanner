import client from './client';
import type { ScreeningResponse, ScreeningResult } from '../types/stock';

export const runScreening = (useMock = true, useLiveData = false, intradayInterval = 1) =>
  client.post<ScreeningResponse>('/screening/run', null, {
    params: { use_mock: useMock, use_live_data: useLiveData, intraday_interval: intradayInterval },
  }).then(r => r.data);

export const getResults = () =>
  client.get<ScreeningResponse>('/screening/results').then(r => r.data);

export const screenSingleStock = (symbol: string, useMock = true) =>
  client.get<ScreeningResult>(`/screening/stock/${symbol}`, {
    params: { use_mock: useMock },
  }).then(r => r.data);
