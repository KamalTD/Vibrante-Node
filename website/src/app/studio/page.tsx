'use client'

import { motion } from 'framer-motion'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { SectionHeader } from '@/components/ui/SectionHeader'

const useCases = [
  {
    title: 'Asset Publishing Automation',
    description:
      'Standardize every publish: version check, file validation, Alembic/USD export, Prism registration, and Deadline submission — in a single repeatable workflow.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
      </svg>
    ),
    color: '#7c3aed',
    tags: ['Prism', 'Deadline', 'USD'],
  },
  {
    title: 'Shot Version Management',
    description:
      'Query every shot in a project, compare published versions against minimum requirements, identify gaps, and generate a report — automatically on every project open.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
    color: '#00d4ff',
    tags: ['Prism', 'Reporting', 'ForEach'],
  },
  {
    title: 'Render Farm Submission',
    description:
      'Build shot lists from CSV or Prism, open each scene, set render settings, batch-submit to Deadline with correct frame ranges and output paths. Zero manual clicking.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
      </svg>
    ),
    color: '#e11d48',
    tags: ['Deadline', 'Houdini', 'Maya'],
  },
  {
    title: 'Multi-DCC Workflows',
    description:
      'Wire Houdini geometry creation directly into Maya rigging pipelines, feed into Blender rendering, and register every intermediate as a Prism product — all in one canvas.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
      </svg>
    ),
    color: '#ff6b35',
    tags: ['Houdini', 'Maya', 'Blender'],
  },
  {
    title: 'USD Pipeline Management',
    description:
      'Create USD layers, set references, author opinions, compose stages, and publish USD assets through Prism — using Vibrante-Node as the visual USD authoring layer.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
      </svg>
    ),
    color: '#34d399',
    tags: ['USD', 'Prism', 'Houdini'],
  },
  {
    title: 'Pipeline Health Monitoring',
    description:
      'Schedule nightly workflows that check project structure, validate file naming conventions, verify Deadline job completion, and send summary reports — automatically.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    color: '#f59e0b',
    tags: ['Automation', 'Monitoring', 'Headless'],
  },
]

const integrationPartners = [
  { name: 'Houdini', color: '#ff6b35', desc: 'Live JSON-RPC bridge', badge: 'Live' },
  { name: 'Maya', color: '#00aeef', desc: 'Headless subprocess', badge: 'Batch' },
  { name: 'Blender', color: '#ea7600', desc: 'Headless subprocess', badge: 'Batch' },
  { name: 'Prism Pipeline', color: '#7c3aed', desc: '60+ native nodes', badge: '60+ nodes' },
  { name: 'Thinkbox Deadline', color: '#e11d48', desc: 'Job submission', badge: 'Render' },
]

const techSpecs = [
  { label: 'Runtime', value: 'Python 3.10+' },
  { label: 'UI Framework', value: 'PyQt5' },
  { label: 'Async Engine', value: 'asyncio + qasync' },
  { label: 'Schema Validation', value: 'Pydantic v2' },
  { label: 'Houdini Protocol', value: 'TCP JSON-RPC' },
  { label: 'Headless Support', value: 'subprocess (mayapy / blender)' },
  { label: 'Node Format', value: 'JSON + Python code string' },
  { label: 'License', value: 'MIT (Open Source)' },
  { label: 'Workflow Format', value: 'JSON (.vnw)' },
  { label: 'Prism Compat.', value: 'Prism 2.x API' },
  { label: 'USD Support', value: 'Via Prism USD integration' },
  { label: 'Execution Model', value: 'Async DAG with exec pins' },
]

export default function StudioPage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-primary/8 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-houdini/5 rounded-full blur-[80px]" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-primary bg-primary/10 border border-primary/20 rounded-full mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                Studio & Pipeline
              </span>
            </motion.div>

            <motion.h1
              className="text-5xl sm:text-6xl font-bold tracking-tight text-text-primary mb-6 leading-tight"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Pipeline Automation
              <br />
              <span className="gradient-text">at Studio Scale</span>
            </motion.h1>

            <motion.p
              className="text-xl text-text-secondary leading-relaxed max-w-2xl mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              From indie studios to large VFX facilities, Vibrante-Node provides the visual workflow layer
              that connects your tools, standardizes your processes, and eliminates manual pipeline work.
            </motion.p>

            <motion.div
              className="flex flex-wrap gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <a
                href="/docs"
                className="inline-flex items-center gap-2 px-7 py-3.5 text-base font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-all hover:shadow-glow-purple"
              >
                Get Started
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
              <a
                href="mailto:contact@vibrante-node.io"
                className="inline-flex items-center gap-2 px-7 py-3.5 text-base font-semibold text-text-primary border border-border hover:border-primary/40 hover:bg-white/5 rounded-xl transition-all"
              >
                Contact Us
              </a>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Use cases grid */}
      <section className="py-24 bg-surface relative">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Studio Use Cases"
            title="What Studios"
            titleGradient="Are Building"
            subtitle="Real automation patterns used in production VFX and animation pipelines."
            align="center"
            className="mb-16"
          />

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {useCases.map((uc, idx) => (
              <motion.div
                key={uc.title}
                className="p-6 rounded-2xl bg-card border border-border hover:border-opacity-60 group transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                whileHover={{ y: -4, borderColor: uc.color + '50' }}
              >
                {/* Icon */}
                <div
                  className="w-11 h-11 rounded-xl flex items-center justify-center mb-4"
                  style={{ background: uc.color + '18', border: `1px solid ${uc.color}30`, color: uc.color }}
                >
                  {uc.icon}
                </div>

                <h3 className="text-base font-bold text-text-primary mb-2">{uc.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed mb-4">{uc.description}</p>

                <div className="flex flex-wrap gap-1.5">
                  {uc.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs font-medium px-2 py-0.5 rounded-full"
                      style={{ background: uc.color + '12', color: uc.color, border: `1px solid ${uc.color}25` }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Integration partners */}
      <section className="py-24 bg-background relative">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Integration Partners"
            title="Your Entire"
            titleGradient="Tool Stack"
            subtitle="Vibrante-Node integrates natively with the tools your studio already uses — no API keys, no SaaS, no subscription."
            align="center"
            className="mb-16"
          />

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {integrationPartners.map((partner, idx) => (
              <motion.div
                key={partner.name}
                className="flex flex-col items-center gap-3 p-6 rounded-2xl bg-card border border-border hover:border-opacity-60 text-center group transition-all"
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.06 }}
                whileHover={{ borderColor: partner.color + '60', y: -4 }}
              >
                {/* Color orb */}
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center"
                  style={{ background: partner.color + '18', border: `2px solid ${partner.color}30` }}
                >
                  <div className="w-6 h-6 rounded-full" style={{ background: partner.color }} />
                </div>

                <div>
                  <p className="font-bold text-text-primary text-sm">{partner.name}</p>
                  <p className="text-xs text-text-secondary mt-0.5">{partner.desc}</p>
                </div>

                <span
                  className="text-xs font-semibold px-2.5 py-1 rounded-full"
                  style={{ background: partner.color + '15', color: partner.color, border: `1px solid ${partner.color}25` }}
                >
                  {partner.badge}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical specs */}
      <section className="py-24 bg-surface relative">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Technical Specs"
            title="Built for"
            titleGradient="Production"
            subtitle="Every technical decision made for reliability, performance, and pipeline compatibility."
            align="center"
            className="mb-16"
          />

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {techSpecs.map((spec, idx) => (
              <motion.div
                key={spec.label}
                className="flex items-start gap-4 p-4 rounded-xl bg-card border border-border"
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: idx * 0.05 }}
              >
                <div className="w-2 h-2 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-0.5">
                    {spec.label}
                  </p>
                  <p className="text-sm font-mono text-text-primary">{spec.value}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-background border-t border-border">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-text-primary mb-4">
            Ready to Automate Your Pipeline?
          </h2>
          <p className="text-text-secondary text-lg mb-8 leading-relaxed">
            Vibrante-Node is open source and free. Download, deploy, and start building automation workflows for your studio today.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <a
              href="/docs"
              className="px-8 py-4 text-base font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-colors hover:shadow-glow-purple"
            >
              Get Started Free
            </a>
            <a
              href="mailto:contact@vibrante-node.io"
              className="px-8 py-4 text-base font-semibold text-text-primary border border-border hover:border-primary/40 rounded-xl transition-colors"
            >
              Talk to the Team
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
