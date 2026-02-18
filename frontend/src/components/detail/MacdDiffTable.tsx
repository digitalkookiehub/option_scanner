import type { MacdHistValue } from '../../types/stock';

export default function MacdDiffTable({ values }: { values: MacdHistValue[] }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-3 text-lg font-semibold">MACD Histogram Values (Last 6 Days)</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-500">
            <th className="py-2">Day</th>
            <th>Date</th>
            <th className="text-right">MACD Hist</th>
            <th className="text-right">Close</th>
            <th className="text-right">Change</th>
          </tr>
        </thead>
        <tbody>
          {values.map((v, i) => {
            const prev = values[i + 1];
            const change = prev ? v.macd_hist - prev.macd_hist : 0;
            return (
              <tr key={i} className="border-b">
                <td className="py-1.5">{v.day === 0 ? 'Today' : `Day -${v.day}`}</td>
                <td>{v.date}</td>
                <td className={`text-right font-mono ${v.macd_hist >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {v.macd_hist.toFixed(4)}
                </td>
                <td className="text-right">{v.close.toFixed(2)}</td>
                <td className={`text-right font-mono ${change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-400'}`}>
                  {i < values.length - 1 ? (change > 0 ? '+' : '') + change.toFixed(4) : '-'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
