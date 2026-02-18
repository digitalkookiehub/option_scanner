export default function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-800">
      <p className="font-medium">Error</p>
      <p className="mt-1 text-sm">{message}</p>
    </div>
  );
}
