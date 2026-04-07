import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'iQuery — Internal Knowledge Chatbot',
  description:
    'Ask questions about your company documents. Powered by RAG — answers grounded in your own uploaded files.',
  keywords: 'document chatbot, RAG, knowledge base, internal search',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full antialiased" style={{ background: 'var(--bg-primary)' }}>
        {children}
      </body>
    </html>
  );
}
