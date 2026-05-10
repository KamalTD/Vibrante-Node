/** @type {import('next').NextConfig} */

const nextConfig = {
  images: {
    unoptimized: true,
  },
  // Allow serving static files from public/
  // Users should copy shots/ folder to website/public/shots/
  // Users should copy logo.png and splash.png to website/public/
}

export default nextConfig
