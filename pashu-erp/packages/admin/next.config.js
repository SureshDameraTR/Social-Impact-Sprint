/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
};

module.exports = nextConfig;
