import Plot from 'react-plotly.js';
import type { IndicatorData } from '../../types/stock';

interface IchimokuMacdChartProps {
  indicators: IndicatorData[];
}

export default function IchimokuMacdChart({ indicators }: IchimokuMacdChartProps) {
  // Last 60 days, ascending order (matching original Streamlit chart)
  const chartData = [...indicators.slice(0, 60)].reverse();

  const dates = chartData.map((d) => d.date);
  const closes = chartData.map((d) => d.close);
  const tenkan = chartData.map((d) => d.tenkan_sen);
  const kijun = chartData.map((d) => d.kijun_sen);
  const spanA = chartData.map((d) => d.senkou_span_a);
  const spanB = chartData.map((d) => d.senkou_span_b);
  const macdHist = chartData.map((d) => d.macd_hist);
  const macdLine = chartData.map((d) => d.macd);
  const signalLine = chartData.map((d) => d.macd_signal);

  const colors = macdHist.map((h) => (h && h >= 0 ? 'green' : 'red'));

  return (
    <Plot
      data={[
        // Price line
        { x: dates, y: closes, name: 'Close Price', type: 'scatter', mode: 'lines', line: { color: 'black', width: 2 }, xaxis: 'x', yaxis: 'y' },
        // Ichimoku lines
        { x: dates, y: tenkan, name: 'Tenkan-sen (Conv.)', type: 'scatter', mode: 'lines', line: { color: 'blue', width: 1 }, xaxis: 'x', yaxis: 'y' },
        { x: dates, y: kijun, name: 'Kijun-sen (Base)', type: 'scatter', mode: 'lines', line: { color: 'red', width: 1 }, xaxis: 'x', yaxis: 'y' },
        // Cloud
        { x: dates, y: spanA, name: 'Senkou Span A', type: 'scatter', mode: 'lines', line: { color: 'green', width: 0.5 }, fill: undefined, xaxis: 'x', yaxis: 'y' },
        { x: dates, y: spanB, name: 'Kumo (Cloud)', type: 'scatter', mode: 'lines', line: { color: 'red', width: 0.5 }, fill: 'tonexty', fillcolor: 'rgba(255,0,0,0.1)', xaxis: 'x', yaxis: 'y' },
        // MACD Histogram
        { x: dates, y: macdHist, name: 'Histogram', type: 'bar', marker: { color: colors }, xaxis: 'x', yaxis: 'y2' },
        // MACD line
        { x: dates, y: macdLine, name: 'MACD Line', type: 'scatter', mode: 'lines', line: { color: 'blue', width: 1 }, xaxis: 'x', yaxis: 'y2' },
        // Signal line
        { x: dates, y: signalLine, name: 'Signal Line', type: 'scatter', mode: 'lines', line: { color: 'orange', width: 1 }, xaxis: 'x', yaxis: 'y2' },
      ]}
      layout={{
        height: 600,
        showlegend: true,
        legend: { orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'right', x: 1 },
        xaxis: { domain: [0, 1], anchor: 'y2', title: { text: 'Date' } },
        yaxis: { domain: [0.35, 1], title: { text: 'Price' }, anchor: 'x' },
        yaxis2: { domain: [0, 0.3], title: { text: 'MACD' }, anchor: 'x' },
        margin: { t: 30, b: 40, l: 60, r: 20 },
        grid: { rows: 2, columns: 1, subplots: [['xy'], ['xy2']] as never, roworder: 'top to bottom' },
      }}
      config={{ responsive: true }}
      style={{ width: '100%' }}
    />
  );
}
