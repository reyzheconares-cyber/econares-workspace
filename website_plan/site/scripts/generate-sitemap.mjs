// scripts/generate-sitemap.mjs — manual sitemap generator (workaround for @astrojs/sitemap bug)
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { resolve, join, relative } from 'node:path';

const DIST = resolve('./dist');
const SITE = 'https://econares.com';

function walk(dir, base = dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const s = statSync(p);
    if (s.isDirectory()) out.push(...walk(p, base));
    else if (name === 'index.html') out.push(p);
  }
  return out;
}

const pages = walk(DIST);
const urls = pages.map(p => {
  const rel = relative(DIST, p).replace(/\\/g, '/').replace(/\/index\.html$/, '') || '/';
  return `<url><loc>${SITE}/${rel}</loc></url>`;
});

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>
`;

writeFileSync(resolve(DIST, 'sitemap.xml'), xml);
console.log(`Wrote ${urls.length} URLs to dist/sitemap.xml`);
