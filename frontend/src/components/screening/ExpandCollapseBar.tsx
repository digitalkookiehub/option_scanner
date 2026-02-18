import { useScreeningStore } from '../../store/screeningStore';

export default function ExpandCollapseBar() {
  const { expandMode, setExpandMode } = useScreeningStore();

  const buttons: { label: string; value: typeof expandMode }[] = [
    { label: 'Collapse All', value: 'none' },
    { label: 'Expand All', value: 'all' },
    { label: 'Bullish Only', value: 'bullish' },
    { label: 'Bearish Only', value: 'bearish' },
  ];

  return (
    <div className="flex gap-2 py-2">
      {buttons.map(({ label, value }) => (
        <button
          key={value}
          onClick={() => setExpandMode(value)}
          className={`rounded px-3 py-1 text-xs font-medium ${
            expandMode === value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
