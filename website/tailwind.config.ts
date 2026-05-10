import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        surface: '#0f0f1a',
        card: '#141428',
        border: '#1e1e3a',
        primary: '#6c63ff',
        secondary: '#00d4ff',
        'text-primary': '#f1f1f3',
        'text-secondary': '#8b8ba7',
        houdini: '#ff6b35',
        maya: '#00aeef',
        blender: '#ea7600',
        prism: '#7c3aed',
        deadline: '#e11d48',
        'pin-string': '#22d3ee',
        'pin-int': '#a78bfa',
        'pin-float': '#34d399',
        'pin-bool': '#f59e0b',
        'pin-list': '#f97316',
        'pin-any': '#6b7280',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        hero: ['72px', { lineHeight: '1.1', fontWeight: '700' }],
        'section-header': ['48px', { lineHeight: '1.2', fontWeight: '600' }],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'grid-pattern': "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231e1e3a' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'flow': 'flow 8s linear infinite',
        'node-activate': 'nodeActivate 0.5s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(108,99,255,0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(108,99,255,0.7)' },
        },
        flow: {
          '0%': { strokeDashoffset: '100' },
          '100%': { strokeDashoffset: '0' },
        },
        nodeActivate: {
          '0%': { filter: 'brightness(1)' },
          '50%': { filter: 'brightness(1.5)' },
          '100%': { filter: 'brightness(1.2)' },
        },
      },
      boxShadow: {
        'glow-purple': '0 0 30px rgba(108,99,255,0.3)',
        'glow-cyan': '0 0 30px rgba(0,212,255,0.3)',
        'glow-orange': '0 0 30px rgba(255,107,53,0.3)',
        'card': '0 4px 24px rgba(0,0,0,0.4)',
      },
    },
  },
  plugins: [],
}

export default config
