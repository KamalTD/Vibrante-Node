'use client'

import { motion } from 'framer-motion'
import { SectionHeader } from '@/components/ui/SectionHeader'

const features = [
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: 'Visual Execution Engine',
    description:
      'Async node execution with exec + data pins. See exactly what runs when. Every node fires in asyncio — the UI never freezes, even during heavy Houdini cooks.',
    color: 'from-primary to-secondary',
    accent: '#6c63ff',
    tag: 'asyncio + qasync',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
      </svg>
    ),
    title: 'Live Wire Inspector',
    description:
      'Hover any wire to see the last value that flowed through it. Debug in seconds, not hours. Values persist after execution for full post-run inspection.',
    color: 'from-secondary to-green-400',
    accent: '#00d4ff',
    tag: 'hover to inspect',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    title: '165+ Built-in Nodes',
    description:
      'Math, logic, file I/O, HTTP, Prism Pipeline, DCC control, ForEach, WhileLoop, SetVariable/GetVariable, SubGraph — and more. Every common pattern is already built in.',
    color: 'from-purple-400 to-primary',
    accent: '#a78bfa',
    tag: '165+ nodes',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
    title: 'Full Python Extensibility',
    description:
      'Any JSON file with a python_code field becomes a node. Drop it in nodes/ and it appears in the library instantly. The Node Builder GUI (Ctrl+E) makes creation visual.',
    color: 'from-green-400 to-secondary',
    accent: '#34d399',
    tag: 'JSON → instant node',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    title: 'Multi-DCC Integration',
    description:
      'Houdini live bridge via TCP JSON-RPC. Maya + Blender via action-list headless subprocess pattern. Prism Pipeline with 60+ nodes. Deadline for render submission.',
    color: 'from-houdini to-yellow-500',
    accent: '#ff6b35',
    tag: 'Houdini · Maya · Blender',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    ),
    title: 'Subgraph / GroupNode',
    description:
      'Collapse any workflow into a reusable component with Ctrl+Shift+G. Share across projects. Nest subgraphs inside subgraphs. Dynamic ports auto-sync with inner connections.',
    color: 'from-primary to-purple-400',
    accent: '#7c3aed',
    tag: 'Ctrl+Shift+G',
  },
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}

const item = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

export function Features() {
  return (
    <section id="features" className="py-24 bg-background relative">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[1px] bg-gradient-to-r from-transparent via-border to-transparent" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Capabilities"
          title="Everything Your Pipeline"
          titleGradient="Needs"
          subtitle="A complete toolkit for VFX automation. From Houdini SOPs to AI orchestration — all in one visual canvas."
          className="mb-16"
        />

        <motion.div
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-100px' }}
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={item}
              className="feature-card relative p-6 rounded-2xl bg-card border border-border hover:border-primary/30 group overflow-hidden"
            >
              {/* Background glow on hover */}
              <div
                className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl"
                style={{
                  background: `radial-gradient(ellipse at 50% 0%, ${feature.accent}15 0%, transparent 70%)`,
                }}
              />

              {/* Icon */}
              <div
                className="relative w-11 h-11 rounded-xl flex items-center justify-center mb-4 text-white"
                style={{ background: `linear-gradient(135deg, ${feature.accent}30, ${feature.accent}10)`, border: `1px solid ${feature.accent}30` }}
              >
                <span style={{ color: feature.accent }}>{feature.icon}</span>
              </div>

              {/* Content */}
              <h3 className="text-base font-semibold text-text-primary mb-2">{feature.title}</h3>
              <p className="text-sm text-text-secondary leading-relaxed">{feature.description}</p>

              {/* Tag */}
              <div className="mt-4">
                <span
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full"
                  style={{
                    background: `${feature.accent}15`,
                    color: feature.accent,
                    border: `1px solid ${feature.accent}30`,
                  }}
                >
                  {feature.tag}
                </span>
              </div>

              {/* Animated corner accent */}
              <div
                className="absolute top-0 right-0 w-20 h-20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{
                  background: `radial-gradient(circle at 100% 0%, ${feature.accent}20 0%, transparent 60%)`,
                }}
              />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
