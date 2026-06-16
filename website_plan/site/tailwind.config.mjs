/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,ts,jsx,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        // ===== ECONARES brand tokens (sourced from ../DESIGN.md) =====
        // Primary structural colors
        primary:    { DEFAULT: '#002A54', 50:'#E6EDF5', 100:'#B3C2D6', 500:'#3D5A82', 700:'#002A54', 900:'#001530' },
        secondary:  { DEFAULT: '#2E343B' },
        ink:        { DEFAULT: '#0E1116' },
        muted:      { DEFAULT: '#4F6876' },
        // Surfaces
        surface:    { DEFAULT: '#F5F5F5' },
        neutral:    { DEFAULT: '#FFFFFF' },
        border:     { DEFAULT: '#D0D5DB' },
        // Brand accents (sparingly — see DESIGN.md §"Composition rule")
        tertiary:   { DEFAULT: '#F5251D' }, // primary CTA / accent
        accent:     { DEFAULT: '#F78D1E' }, // CTA hover / focus ring
        highlight:  { DEFAULT: '#FDE126' }, // tag/ribbon only — never body
        sky:        { DEFAULT: '#6DA6E3' }, // footer link / info bg
        blue:       { DEFAULT: '#0033FF' }, // body link / in-text emphasis
        green:      { DEFAULT: '#6AFE01' }, // trust badge / success
        // Logo illustration accents
        tan:        { DEFAULT: '#A98F7A' },
        khaki:      { DEFAULT: '#DCD3A6' },
        // Kami (parchment) palette — concept B
        parchment:    { DEFAULT: '#F5F4ED' },
        'parchment-2':{ DEFAULT: '#EAE7DC' },
        'ink-blue':   { DEFAULT: '#1B365D' },
        'ink-blue-tint':{ DEFAULT: '#E4ECF5' },
        olive:        { DEFAULT: '#5B5A3E' },
        rust:         { DEFAULT: '#8C4A2B' },
      },
      fontFamily: {
        display: ['Montserrat', 'system-ui', 'sans-serif'],
        body:    ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        tag:     ['"Barlow Condensed"', 'sans-serif'],
        serif:   ['Charter', '"Bitstream Charter"', '"Iowan Old Style"', 'Georgia', '"Times New Roman"', 'serif'],
      },
      borderRadius: {
        sm: '4px', md: '8px', lg: '12px', pill: '9999px',
      },
      boxShadow: {
        card:     '0 1px 3px rgba(14,17,22,.08), 0 1px 2px rgba(14,17,22,.04)',
        'card-h': '0 10px 25px rgba(14,17,22,.10), 0 4px 10px rgba(14,17,22,.04)',
        sticky:   '0 2px 8px rgba(14,17,22,.06)',
        whisper:  '0 4px 24px rgba(0,0,0,0.05)',
      },
      maxWidth: {
        container: '1280px',
        prose:      '720px',
      },
      letterSpacing: {
        tag: '0.08em',
        eyebrow: '0.14em',
      },
    },
  },
  plugins: [],
};
