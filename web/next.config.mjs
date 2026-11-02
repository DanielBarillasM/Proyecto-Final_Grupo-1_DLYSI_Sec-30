/** @type {import('next').NextConfig} */
const allowedDevOrigins = (process.env.NEXT_ALLOWED_DEV_ORIGINS ?? '')
  .split(',')
  .map((origin) => origin.trim())
  .filter(Boolean)

const nextConfig = {
  images: { unoptimized: true },
  allowedDevOrigins,
}

export default nextConfig
