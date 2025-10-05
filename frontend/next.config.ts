import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ['lh3.googleusercontent.com', 'firebasestorage.googleapis.com'],
  },
  // Allow build to continue with TypeScript errors
  typescript: {
    ignoreBuildErrors: true,
  },
  // Allow build to continue with ESLint errors
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    // Only use localhost rewrites in development
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ]
    }
    return [];
  },
};

export default nextConfig;
