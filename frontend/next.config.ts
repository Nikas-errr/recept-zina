import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    allowedDevOrigins: ['toughly-laureate-pheasant.cloudpub.ru'],
    images: {
        remotePatterns: [
            { protocol: 'https', hostname: 'www.themealdb.com' },
        ],
    },
    turbopack: {
        rules: {
            "*.css": {
                loaders: ["@tailwindcss/turbopack"],
                as: "*.css",
            },
        },
    },
};

export default nextConfig;
