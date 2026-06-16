// src/data/loader.js — load and validate the YAML data files
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import yaml from 'js-yaml';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = resolve(__dirname, '../../../');

// Lightweight loader — strips any non-serializable Yaml types
function loadYaml(filename) {
  const path = resolve(DATA_DIR, filename);
  const raw = readFileSync(path, 'utf8');
  return yaml.load(raw, { schema: yaml.JSON_SCHEMA });
}

export const products = loadYaml('products.yaml').products ?? [];
export const services = loadYaml('services.yaml').services ?? [];
export const projects = loadYaml('projects.yaml').projects ?? [];

// Derived lookups
export const productBySlug = Object.fromEntries(products.map(p => [p.slug, p]));
export const serviceBySlug = Object.fromEntries(services.map(s => [s.slug, s]));
export const projectBySlug = Object.fromEntries(projects.map(p => [p.slug, p]));

// Related products: same category, exclude self
export function relatedProducts(slug, limit = 4) {
  const me = productBySlug[slug];
  if (!me) return [];
  return products
    .filter(p => p.slug !== slug && p.category === me.category)
    .slice(0, limit);
}

// Sub-services for a service category
export function subServices(slug) {
  const me = serviceBySlug[slug];
  return me?.sub_services ?? [];
}

// All sub-services flattened (for "all services" footer listing)
export function allSubServices() {
  return services.flatMap(s => (s.sub_services ?? []).map(sub => ({ ...sub, parent: s.slug, parentName: s.name })));
}
