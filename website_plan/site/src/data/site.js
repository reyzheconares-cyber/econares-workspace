// src/data/site.js — single source of truth for site identity
// Mirrors the brand block of ../DESIGN.md

export const SITE = {
  name: 'ECONARES',
  legal: 'ECE Construction and Resources OPC',
  tagline: 'CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING',
  acronym: 'Excellent products & services · Corporate social and environmental responsibility · Economic development share',
  url: 'https://econares.com',
  description: 'A SEC-registered Philippine supplier of industrial fuels and metallic & non-metallic minerals, with a PCAB-licensed construction arm. Serving cement, sugar, power, and manufacturing industries from Cebu since 2015.',
  address: {
    street: 'G/F BT & T Bldg., Hollow Block Road',
    locality: 'Tabunok, Talisay City, Cebu 6045',
    country: 'Philippines',
  },
  phone: '(+63 32) 232 6280',
  phoneTel: '+6332322326280',
  email: 'ece.eleguinresources@yahoo.com',
  whatsapp: '639171234567',
  founded: 2015,
  social: {
    linkedin: 'https://www.linkedin.com/company/econares',
  },
  credentials: [
    'SEC-Registered OPC',
    'DTI 2015 · ECE Resources',
    'DTI 2019 · ECE Construction',
    'PCAB Licensed',
    '15+ Years in PH Heavy Industry',
  ],
};

export const NAV = [
  { href: '/', label: 'Home' },
  { href: '/about/', label: 'About' },
  { href: '/products/', label: 'Products' },
  { href: '/services/', label: 'Services' },
  { href: '/projects/', label: 'Projects' },
  { href: '/capabilities/', label: 'Capabilities' },
  { href: '/insights/', label: 'Insights' },
  { href: '/contact/', label: 'Contact' },
];
