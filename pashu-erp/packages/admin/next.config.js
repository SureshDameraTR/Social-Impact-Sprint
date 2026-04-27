/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
};

module.exports = nextConfig;
