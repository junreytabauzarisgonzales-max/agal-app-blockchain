import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static marketing site, no server-side logic -- ships as plain HTML/CSS/JS.
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
