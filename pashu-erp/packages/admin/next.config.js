/** @type {import('next').NextConfig} */
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// CSP connect-src needs the origin (not path) to allow all API sub-paths
const apiOrigin = (() => { try { return new URL(apiUrl).origin; } catch { return apiUrl; } })();

const nextConfig = {
  output: "standalone",
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
  images: {
    formats: ["image/avif", "image/webp"],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(self), payment=()",
          },
          {
            key: "Cross-Origin-Opener-Policy",
            value: "same-origin",
          },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              `script-src 'self'${process.env.NODE_ENV === 'development' ? " 'unsafe-eval' 'unsafe-inline'" : ''}`,
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com",
              "img-src 'self' data: blob: https://*.tile.openstreetmap.org https://unpkg.com https://telemetry.refine.dev",
              "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com",
              `connect-src 'self' ${apiOrigin}${process.env.NODE_ENV === 'development' ? ' ws://localhost:3000' : ''}`,
              "frame-ancestors 'none'",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
