import { type ReactNode } from 'react';
import Header from './Header';

export default function PageLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex flex-1">{children}</main>
    </div>
  );
}
