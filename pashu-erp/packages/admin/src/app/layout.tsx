import Providers from "./providers";

export const metadata = {
  title: "PashuRaksha ERP - Admin Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+Kannada:wght@400;500;600&display=swap" rel="stylesheet" />
        <style>{`
          .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #0f2b24;
            color: #ffffff;
            padding: 8px 16px;
            z-index: 9999;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            border-radius: 0 0 4px 0;
            transition: top 0.2s;
          }
          .skip-link:focus {
            top: 0;
          }
        `}</style>
      </head>
      <body suppressHydrationWarning style={{ margin: 0, backgroundColor: '#f0f4f3' }}>
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
