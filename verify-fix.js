const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const shotsDir = '/workspace/debug-shots';
if (!fs.existsSync(shotsDir)) fs.mkdirSync(shotsDir, { recursive: true });

const pages = [
  {
    name: '01-shokugeki-top',
    url: 'http://localhost:8000/content/shokugeki-no-soma/arc-01-enrollment.html',
    scroll: 0,
    wait: 1500,
  },
  {
    name: '02-shokugeki-side-toc-visible',
    url: 'http://localhost:8000/content/shokugeki-no-soma/arc-01-enrollment.html',
    scroll: 100,
    wait: 1000,
  },
  {
    name: '03-maoyuu-header-visible',
    url: 'http://localhost:8000/content/maoyuu-political-economy/index.html',
    scroll: 0,
    wait: 1500,
  },
  {
    name: '04-maoyuu-narrative-top',
    url: 'http://localhost:8000/content/maoyuu-political-economy/narrative-analysis.html',
    scroll: 0,
    wait: 1500,
  },
  {
    name: '05-maoyuu-chart-timeline',
    url: 'http://localhost:8000/content/maoyuu-political-economy/narrative-analysis.html',
    scroll: 2200,
    wait: 1000,
  },
  {
    name: '06-maoyuu-chart-network',
    url: 'http://localhost:8000/content/maoyuu-political-economy/narrative-analysis.html',
    scroll: 3500,
    wait: 1000,
  },
];

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  for (const p of pages) {
    console.log(`Opening ${p.name} ...`);
    await page.goto(p.url, { waitUntil: 'networkidle' });
    await page.evaluate((scroll) => window.scrollTo(0, scroll), p.scroll);
    await page.waitForTimeout(p.wait);
    const shotPath = `${shotsDir}/${p.name}.png`;
    await page.screenshot({ path: shotPath });
    console.log(`  Saved: ${shotPath}`);
  }

  await browser.close();
  console.log('Done.');
})();
