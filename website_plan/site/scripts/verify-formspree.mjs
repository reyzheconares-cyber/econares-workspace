// Verify Formspree wiring for ECONARES RFQ forms.
// This checks source and built output so placeholder regressions are caught.
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const root = process.cwd();
const endpoint = 'https://formspree.io/f/mlgkvevq';
const sourcePath = resolve(root, 'src/pages/contact.astro');
const builtPath = resolve(root, 'dist/contact/index.html');

function fail(message) {
  console.error(`FAIL: ${message}`);
  process.exitCode = 1;
}

function count(haystack, needle) {
  return haystack.split(needle).length - 1;
}

const source = readFileSync(sourcePath, 'utf8');

if (source.includes('PLACEHOLDER')) fail('source still contains PLACEHOLDER');
if (count(source, endpoint) < 1) fail('source does not define/use the real Formspree endpoint');
if (!source.includes('name="_subject" value="ECONARES Product RFQ"')) fail('product RFQ lacks tailored _subject');
if (!source.includes('name="_subject" value="ECONARES Service RFQ"')) fail('service RFQ lacks tailored _subject');
if (count(source, 'name="_gotcha"') !== 2) fail('both forms must include Formspree honeypot _gotcha');
if (count(source, 'method="POST"') !== 2) fail('both forms must POST');

if (existsSync(builtPath)) {
  const built = readFileSync(builtPath, 'utf8');
  if (built.includes('PLACEHOLDER')) fail('built contact page still contains PLACEHOLDER');
  if (count(built, endpoint) !== 2) fail(`built contact page should contain endpoint twice, found ${count(built, endpoint)}`);
  if (!built.includes('ECONARES Product RFQ')) fail('built contact page lacks product _subject');
  if (!built.includes('ECONARES Service RFQ')) fail('built contact page lacks service _subject');
}

if (!process.exitCode) console.log('Formspree wiring OK');
