export default function ScreeningProgress() {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      <p className="mt-4 text-gray-600">Screening 211 stocks...</p>
      <p className="text-sm text-gray-400">Analyzing Ichimoku Cloud + MACD indicators</p>
    </div>
  );
}
