'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Image from 'next/image'
import { SectionHeader } from '@/components/ui/SectionHeader'

const screenshots = [
  {
    src: '/shots/07.PNG',
    alt: 'Vibrante-Node — Full node graph with Houdini pipeline workflow',
    caption: 'Visual node canvas with exec pins and data wires',
    tag: 'Node Canvas',
  },
  {
    src: '/shots/08.PNG',
    alt: 'Vibrante-Node — Workflow example with multiple connected nodes',
    caption: 'Complex multi-node workflows with ForEach loops and logic branching',
    tag: 'Workflow',
  },
  {
    src: '/shots/04.PNG',
    alt: 'Vibrante-Node — UI screenshot showing node library panel',
    caption: 'Node library with 165+ categorized built-in nodes',
    tag: 'Library',
  },
  {
    src: '/shots/05.PNG',
    alt: 'Vibrante-Node — UI screenshot showing execution log',
    caption: 'Real-time execution log with per-node timing',
    tag: 'Execution',
  },
  {
    src: '/shots/06.PNG',
    alt: 'Vibrante-Node — UI screenshot showing properties panel',
    caption: 'Node properties panel with type-aware widgets',
    tag: 'Properties',
  },
]

export function Screenshots() {
  const [active, setActive] = useState(0)
  const [lightboxOpen, setLightboxOpen] = useState(false)

  return (
    <section id="screenshots" className="py-24 bg-surface relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[1px] bg-gradient-to-r from-transparent via-border to-transparent" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Screenshots"
          title="See It"
          titleGradient="In Action"
          subtitle="A production-grade desktop app built with PyQt5. Dark theme, mini-map, canvas search, autosave — all included."
          className="mb-12"
        />

        {/* Main screenshot */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Large preview */}
          <div className="lg:col-span-2">
            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.25 }}
                className="relative rounded-2xl overflow-hidden border border-border bg-background cursor-pointer screenshot-card group"
                onClick={() => setLightboxOpen(true)}
              >
                {/* Window chrome */}
                <div className="flex items-center gap-2 px-4 py-2.5 bg-surface border-b border-border">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/70" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                    <div className="w-3 h-3 rounded-full bg-green-500/70" />
                  </div>
                  <span className="text-xs text-text-secondary font-mono flex-1 text-center">
                    Vibrante-Node — {screenshots[active].tag}
                  </span>
                </div>

                <div className="relative aspect-video bg-background">
                  <Image
                    src={screenshots[active].src}
                    alt={screenshots[active].alt}
                    fill
                    className="object-cover object-top"
                    sizes="(max-width: 768px) 100vw, 66vw"
                    priority={active === 0}
                  />
                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 backdrop-blur-sm rounded-xl px-4 py-2 flex items-center gap-2">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                      </svg>
                      <span className="text-sm text-white font-medium">Zoom</span>
                    </div>
                  </div>
                </div>

                {/* Caption */}
                <div className="px-4 py-3 bg-card flex items-center justify-between">
                  <p className="text-sm text-text-secondary">{screenshots[active].caption}</p>
                  <span className="text-xs text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded-full">
                    {screenshots[active].tag}
                  </span>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Thumbnails */}
          <div className="flex lg:flex-col gap-3 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0">
            {screenshots.map((shot, idx) => (
              <button
                key={idx}
                className={`flex-shrink-0 w-36 lg:w-full rounded-xl overflow-hidden border-2 transition-all duration-200 ${
                  active === idx
                    ? 'border-primary shadow-glow-purple'
                    : 'border-border hover:border-primary/40'
                }`}
                onClick={() => setActive(idx)}
              >
                <div className="relative aspect-video bg-background">
                  <Image
                    src={shot.src}
                    alt={shot.alt}
                    fill
                    className="object-cover object-top"
                    sizes="144px"
                  />
                  {active === idx && (
                    <div className="absolute inset-0 bg-primary/10" />
                  )}
                </div>
                <div className="px-2 py-1.5 bg-card text-left">
                  <p className="text-xs text-text-secondary truncate">{shot.tag}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Keyboard shortcut hints */}
        <motion.div
          className="mt-10 flex flex-wrap justify-center gap-4"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          {[
            { key: 'Ctrl+F', desc: 'Canvas Search' },
            { key: 'Ctrl+M', desc: 'Toggle Mini-map' },
            { key: 'Ctrl+Shift+G', desc: 'Group Selection' },
            { key: 'Ctrl+E', desc: 'Node Builder' },
            { key: 'Ctrl+Z', desc: 'Undo / Redo' },
          ].map(({ key, desc }) => (
            <div key={key} className="flex items-center gap-2 text-sm text-text-secondary">
              <kbd className="px-2 py-0.5 text-xs font-mono bg-card border border-border rounded-md text-text-primary">
                {key}
              </kbd>
              <span>{desc}</span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Lightbox */}
      <AnimatePresence>
        {lightboxOpen && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setLightboxOpen(false)}
          >
            <motion.div
              className="relative max-w-6xl w-full rounded-2xl overflow-hidden"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <Image
                src={screenshots[active].src}
                alt={screenshots[active].alt}
                width={1280}
                height={720}
                className="w-full h-auto"
              />
              <button
                className="absolute top-4 right-4 w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white hover:bg-black/80 transition-colors"
                onClick={() => setLightboxOpen(false)}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  )
}
