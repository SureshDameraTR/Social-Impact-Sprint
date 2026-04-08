/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
  experimental: {
    // Enable server actions if needed
  },
};

module.exports = nextConfig;
