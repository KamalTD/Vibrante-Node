import type { Metadata } from 'next'
import './globals.css'
import 'highlight.js/styles/github-dark.css'

export const metadata: Metadata = {
  title: 'Vibrante-Node — Visual Workflow Automation for VFX & AI Pipelines',
  description:
    'Python-node-based visual framework for building modular systems through connected nodes and data flows. Visual pipelines, automation workflows, and data-processing graphs.',
  keywords: [
    'VFX pipeline',
    'node-based automation',
    'Houdini pipeline',
    'visual scripting',
    'AI workflow',
    'pipeline automation',
    'USD pipeline',
    'Maya pipeline',
    'Blender automation',
    'Prism Pipeline',
    'visual programming',
    'Python automation',
  ],
  authors: [{ name: 'Vibrante-Node Team' }],
  creator: 'Vibrante-Node',
  publisher: 'Vibrante-Node',
  metadataBase: new URL('https://vibrante-node.io'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://vibrante-node.io',
    title: 'Vibrante-Node — Visual Workflow Automation for VFX & AI Pipelines',
    description:
      'Python-node-based visual framework for building modular systems through connected nodes and data flows. Visual pipelines, automation workflows, and data-processing graphs.',
    siteName: 'Vibrante-Node',
    images: [
      {
        url: '/shots/07.PNG',
        width: 1280,
        height: 720,
        alt: 'Vibrante-Node — Visual Workflow Automation',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Vibrante-Node — Visual Workflow Automation for VFX & AI Pipelines',
    description:
      'Python-node-based visual framework for building modular systems through connected nodes and data flows. Visual pipelines, automation workflows, and data-processing graphs.',
    images: ['/shots/07.PNG'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/icons/vibrante-node-icon.png',
    shortcut: '/icons/vibrante-node-icon.png',
    apple: '/icons/vibrante-node-icon.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background text-text-primary antialiased">
        {children}
      </body>
    </html>
  )
}
