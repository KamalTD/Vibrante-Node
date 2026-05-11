'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { NodeGraphSVG } from './NodeGraphSVG'

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-16">
      {/* Background gradients */}
      <div className="absolute inset-0 bg-background" />
      <div className="absolute inset-0 bg-grid opacity-40" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[600px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 right-0 w-[400px] h-[400px] bg-secondary/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-houdini/5 rounded-full blur-[80px] pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Text column */}
          <div className="flex flex-col gap-6">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="flex items-center gap-3"
            >
              <span className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-primary bg-primary/10 border border-primary/20 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                Open Source · v2.0.0
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-text-secondary bg-white/5 border border-border rounded-full">
                Python 3.10+ · PyQt5
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.08]"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <span className="text-text-primary">Build Production</span>
              <br />
              <span className="gradient-text">Workflows at the</span>
              <br />
              <span className="text-text-primary">Speed of Thought</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              className="text-lg text-text-secondary leading-relaxed max-w-xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.35 }}
            >
              Vibrante-Node is a Python-node-based visual framework for building modular systems
              through connected nodes and data flows. It provides an intuitive graph interface where
              complex logic can be constructed visually by linking nodes together.{' '}
              The project focuses on flexibility, extensibility, and developer productivity, making
              it suitable for building tools such as visual pipelines, automation workflows, and
              data-processing graphs. Node-based systems allow complex operations to be organized as
              interconnected components rather than traditional linear code structures, improving
              clarity and scalability in large workflows.
            </motion.p>

            {/* CTA buttons */}
            <motion.div
              className="flex flex-wrap gap-4 mt-2"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.45 }}
            >
              <Link
                href="/docs"
                className="inline-flex items-center gap-2 px-7 py-3.5 text-base font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-all duration-200 hover:shadow-glow-purple hover:-translate-y-0.5"
              >
                Get Started Free
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <Link
                href="/docs"
                className="inline-flex items-center gap-2 px-7 py-3.5 text-base font-semibold text-primary border border-primary/40 hover:border-primary hover:bg-primary/5 rounded-xl transition-all duration-200"
              >
                View Documentation
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </Link>
            </motion.div>

            {/* Stats */}
            <motion.div
              className="flex flex-wrap gap-8 pt-4 border-t border-border/50 mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              {[
                { label: 'Built-in Nodes', value: '165+' },
                { label: 'DCC Integrations', value: '5' },
                { label: 'Python API', value: '100%' },
                { label: 'License', value: 'MIT' },
              ].map((stat) => (
                <div key={stat.label} className="flex flex-col gap-0.5">
                  <span className="text-2xl font-bold text-text-primary">{stat.value}</span>
                  <span className="text-xs text-text-secondary">{stat.label}</span>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Node graph animation column */}
          <motion.div
            className="relative lg:block"
            initial={{ opacity: 0, scale: 0.95, x: 20 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
          >
            <div className="relative">
              {/* Outer glow */}
              <div className="absolute -inset-4 bg-primary/10 rounded-3xl blur-2xl" />
              {/* Border frame */}
              <div className="relative rounded-2xl overflow-hidden border border-border/80 shadow-2xl bg-background">
                {/* Window chrome */}
                <div className="flex items-center gap-2 px-4 py-3 bg-surface border-b border-border">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/70" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                    <div className="w-3 h-3 rounded-full bg-green-500/70" />
                  </div>
                  <div className="flex-1 mx-4">
                    <div className="h-5 flex items-center bg-background/60 rounded-md px-3">
                      <div className="w-2 h-2 rounded-full bg-primary/60 mr-2" />
                      <span className="text-xs text-text-secondary font-mono">vibrante-node — houdini_asset_pipeline.vnw</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-text-secondary font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                    Running
                  </div>
                </div>
                <div className="aspect-[4/3]">
                  <NodeGraphSVG />
                </div>
              </div>

              {/* Floating info badges */}
              <motion.div
                className="absolute -left-6 top-1/4 glass-card rounded-xl px-3 py-2 shadow-lg"
                animate={{ y: [0, -6, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              >
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-houdini/20 flex items-center justify-center">
                    <div className="w-3 h-3 rounded-full bg-houdini" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-text-primary">Houdini Bridge</div>
                    <div className="text-[10px] text-houdini">Connected ✓</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                className="absolute -right-4 bottom-1/3 glass-card rounded-xl px-3 py-2 shadow-lg"
                animate={{ y: [0, 6, 0] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
              >
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-secondary/20 flex items-center justify-center">
                    <svg className="w-3 h-3 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-text-primary">Async Engine</div>
                    <div className="text-[10px] text-secondary">0 UI freeze</div>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <span className="text-xs text-text-secondary/60">Scroll to explore</span>
        <motion.div
          className="w-5 h-8 rounded-full border border-border/60 flex items-center justify-center"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <motion.div
            className="w-1 h-2 rounded-full bg-primary/60"
            animate={{ y: [0, 4, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </motion.div>
      </motion.div>
    </section>
  )
}
