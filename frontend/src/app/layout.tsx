import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CryptoSignal — Command Center',
  description: 'Institutional-grade crypto trading platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-surface text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
