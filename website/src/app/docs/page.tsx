'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { docSections } from '@/components/docs/docSections'

export default function DocsPage() {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredSections = docSections.filter(
    (s) =>
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.items.some((item) => item.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="pt-16 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-4 gap-0 min-h-screen">
            {/* Sidebar */}
            <aside className="lg:col-span-1 border-r border-border pt-8 pb-8 pr-0 lg:pr-6">
              {/* Header */}
              <div className="mb-6">
                <h1 className="text-xl font-bold text-text-primary mb-1">Documentation</h1>
                <p className="text-sm text-text-secondary">v2.0.0</p>
              </div>

              {/* Search */}
              <div className="relative mb-4">
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search docs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 text-sm bg-card border border-border rounded-xl text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/20 transition-all"
                />
              </div>

              {/* Nav sections */}
              <nav className="flex flex-col gap-0.5">
                {filteredSections.map((section) => (
                  <Link
                    key={section.id}
                    href={`/docs/${section.id}`}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left text-sm transition-all duration-150 text-text-secondary hover:text-text-primary hover:bg-white/5"
                  >
                    <span className="text-base">{section.icon}</span>
                    <span className="truncate">{section.title}</span>
                  </Link>
                ))}
              </nav>

              {filteredSections.length === 0 && (
                <p className="text-sm text-text-secondary text-center py-8">
                  No results for &quot;{searchQuery}&quot;
                </p>
              )}
            </aside>

            {/* Main content — index overview */}
            <motion.main
              className="lg:col-span-3 pt-8 pb-16 lg:pl-10"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
            >
              {/* Header */}
              <div className="mb-8">
                <h1 className="text-4xl font-bold text-text-primary mb-3">
                  Vibrante-Node Documentation
                </h1>
                <p className="text-lg text-text-secondary">
                  Full reference for v2.0.0 — 14 chapters covering installation, node development,
                  Houdini integration, and the full Python API.
                </p>
              </div>

              <div className="border-t border-border mb-8" />

              {/* Quick start cards */}
              <div className="grid sm:grid-cols-3 gap-4 mb-10">
                {[
                  { href: '/docs/getting-started', icon: '🚀', label: 'Quick Start', desc: 'Install and run in 5 minutes' },
                  { href: '/docs/node-development', icon: '🔧', label: 'Build a Node', desc: 'JSON + Python in one file' },
                  { href: '/docs/api-reference', icon: '📚', label: 'API Reference', desc: 'BaseNode, HouBridge, Prism' },
                ].map((card) => (
                  <Link
                    key={card.href}
                    href={card.href}
                    className="flex flex-col gap-2 p-5 rounded-2xl bg-card border border-border hover:border-primary/30 hover:bg-primary/5 transition-all group"
                  >
                    <span className="text-3xl">{card.icon}</span>
                    <span className="text-sm font-semibold text-text-primary group-hover:text-primary transition-colors">
                      {card.label}
                    </span>
                    <span className="text-xs text-text-secondary">{card.desc}</span>
                  </Link>
                ))}
              </div>

              {/* All sections grid */}
              <h2 className="text-lg font-bold text-text-primary mb-4">All Documentation Sections</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {docSections.map((section) => (
                  <Link
                    key={section.id}
                    href={`/docs/${section.id}`}
                    className="flex items-start gap-3 p-4 rounded-xl border border-border bg-card hover:border-primary/20 hover:bg-primary/5 text-left transition-all group"
                  >
                    <span className="text-2xl flex-shrink-0">{section.icon}</span>
                    <div>
                      <p className="text-sm font-semibold text-text-primary group-hover:text-primary transition-colors">
                        {section.title}
                      </p>
                      <p className="text-xs text-text-secondary mt-0.5 line-clamp-2">{section.summary}</p>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Footer links */}
              <div className="mt-10 pt-8 border-t border-border flex items-center justify-between">
                <div className="text-sm text-text-secondary">
                  Found an issue?{' '}
                  <a href="https://github.com/vibrante-node" className="text-primary hover:underline">
                    Open a GitHub issue
                  </a>
                </div>
                <a
                  href="https://github.com/vibrante-node"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                  View on GitHub
                </a>
              </div>
            </motion.main>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
