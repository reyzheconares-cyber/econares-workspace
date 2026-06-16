import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://econares.com',
  integrations: [
    tailwind({ applyBaseStyles: true }),
  ],
  build: {
    inlineStylesheets: 'auto',
  },
  vite: {
    server: { host: '127.0.0.1', port: 4321, strictPort: true },
  },
});
