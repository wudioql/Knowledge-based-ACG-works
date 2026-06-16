import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// 环境变量 BASE_PATH 覆盖默认值（用于 GitHub Pages 部署）
// 本地开发（npm run dev）时可以留空，默认使用仓库名作为 base
const DEFAULT_BASE = '/Knowledge-based_ACG_Astro_Wiki/';
const base = process.env.BASE_PATH || DEFAULT_BASE;
const site = process.env.SITE_URL || 'https://example.github.io';

export default defineConfig({
  site,
  base,
  integrations: [mdx()],
  output: 'static',
  build: {
    format: 'directory',
  },
});
