import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* The dev indicator defaults to bottom-left, where it covers the knowledge
     graph ledger at the foot of the nav rail. */
  devIndicators: { position: "bottom-right" },
};

export default nextConfig;
