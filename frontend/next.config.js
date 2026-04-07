/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow API calls to the backend in development
  async rewrites() {
    return process.env.NODE_ENV === 'development'
      ? [
          {
            source: '/api/:path*',
            destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
          },
        ]
      : [];
  },
};

module.exports = nextConfig;
