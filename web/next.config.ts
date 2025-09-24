import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next serves files from /public, we symlink /apk -> /public/apk in Dockerfile
};

export default nextConfig;
