'use client'

import { motion } from 'framer-motion'
import { SectionHeader } from '@/components/ui/SectionHeader'

interface MiniNode {
  x: number
  y: number
  label: string
  color: string
}

interface MiniEdge {
  x1: number
  y1: number
  x2: number
  y2: number
}

function MiniGraph({ nodes, edges }: { nodes: MiniNode[]; edges: MiniEdge[] }) {
  return (
    <svg viewBox="0 0 240 80" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
      <rect width="240" height="80" rx="8" fill="#0a0a0f" />
      <pattern id="mgrid" width="16" height="16" patternUnits="userSpaceOnUse">
        <path d="M 16 0 L 0 0 0 16" fill="none" stroke="#1e1e3a" strokeWidth="0.3" />
      </pattern>
      <rect width="240" height="80" rx="8" fill="url(#mgrid)" />
      {/* Edges */}
      {edges.map((e, i) => (
        <path
          key={i}
          d={`M ${e.x1} ${e.y1} C ${(e.x1 + e.x2) / 2} ${e.y1}, ${(e.x1 + e.x2) / 2} ${e.y2}, ${e.x2} ${e.y2}`}
          fill="none"
          stroke="#2a2a4a"
          strokeWidth="1.5"
          strokeDasharray="4 3"
        />
      ))}
      {/* Nodes */}
      {nodes.map((n, i) => (
        <g key={i}>
          <rect
            x={n.x - 30}
            y={n.y - 10}
            width="60"
            height="20"
            rx="4"
            fill="#141428"
            stroke={n.color}
            strokeWidth="0.8"
            strokeOpacity="0.6"
          />
          <rect
            x={n.x - 30}
            y={n.y - 10}
            width="2"
            height="20"
            rx="2"
            fill={n.color}
            opacity="0.8"
          />
          <text
            x={n.x - 6}
            y={n.y + 4}
            fontSize="5.5"
            fill="#c5c5d2"
            fontFamily="'JetBrains Mono', monospace"
          >
            {n.label}
          </text>
          {/* Output exec pin */}
          <rect
            x={n.x + 27}
            y={n.y - 3}
            width="5"
            height="5"
            rx="1"
            fill="#3a3a5a"
            stroke="#4a4a6a"
            strokeWidth="0.4"
          />
        </g>
      ))}
    </svg>
  )
}

const workflows = [
  {
    title: 'VFX Asset Publishing',
    description:
      'Prism nodes query assets, check versions, export to USD, and submit to Deadline. One workflow, zero manual steps.',
    color: '#7c3aed',
    nodes: [
      { x: 30, y: 40, label: 'Get Asset', color: '#7c3aed' },
      { x: 90, y: 40, label: 'Check Ver', color: '#7c3aed' },
      { x: 150, y: 25, label: 'Export USD', color: '#34d399' },
      { x: 150, y: 55, label: 'Submit Job', color: '#e11d48' },
      { x: 210, y: 40, label: 'Log Done', color: '#34d399' },
    ],
    edges: [
      { x1: 60, y1: 40, x2: 60, y2: 40 },
      { x1: 57, y1: 40, x2: 63, y2: 40 },
      { x1: 117, y1: 40, x2: 123, y2: 25 },
      { x1: 117, y1: 40, x2: 123, y2: 55 },
      { x1: 177, y1: 25, x2: 183, y2: 40 },
      { x1: 177, y1: 55, x2: 183, y2: 40 },
    ],
    tags: ['prism_get_assets', 'prism_check_version', 'usd_export', 'deadline_submit'],
  },
  {
    title: 'Houdini Procedural Network',
    description:
      'Create geo networks, wire SOPs, set parameters, cook, and save .hip files — all via the JSON-RPC bridge to a live session.',
    color: '#ff6b35',
    nodes: [
      { x: 30, y: 40, label: 'Create Geo', color: '#ff6b35' },
      { x: 90, y: 40, label: 'Create SOP', color: '#ff6b35' },
      { x: 150, y: 40, label: 'Set Parms', color: '#ff6b35' },
      { x: 210, y: 40, label: 'Cook Node', color: '#ff6b35' },
    ],
    edges: [
      { x1: 57, y1: 40, x2: 63, y2: 40 },
      { x1: 117, y1: 40, x2: 123, y2: 40 },
      { x1: 177, y1: 40, x2: 183, y2: 40 },
    ],
    tags: ['hou_create_node', 'hou_set_parm', 'hou_cook_node', 'hou_save_hip'],
  },
  {
    title: 'AI Pipeline Orchestration',
    description:
      'Chain LLM calls, process responses, route on sentiment, write to database. Build multi-step AI workflows visually.',
    color: '#00d4ff',
    nodes: [
      { x: 30, y: 40, label: 'HTTP Call', color: '#22d3ee' },
      { x: 90, y: 40, label: 'Parse JSON', color: '#a78bfa' },
      { x: 150, y: 25, label: 'If Branch', color: '#a78bfa' },
      { x: 150, y: 55, label: 'Log Error', color: '#e11d48' },
      { x: 210, y: 25, label: 'Write DB', color: '#34d399' },
    ],
    edges: [
      { x1: 57, y1: 40, x2: 63, y2: 40 },
      { x1: 117, y1: 40, x2: 123, y2: 25 },
      { x1: 117, y1: 40, x2: 123, y2: 55 },
      { x1: 177, y1: 25, x2: 183, y2: 25 },
    ],
    tags: ['http_request', 'json_parse', 'if_else', 'foreach', 'write_file'],
  },
]

export function WorkflowShowcase() {
  return (
    <section className="py-24 bg-surface relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[1px] bg-gradient-to-r from-transparent via-border to-transparent" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Use Cases"
          title="Workflows That"
          titleGradient="Ship Pipelines"
          subtitle="From Houdini procedurals to AI orchestration — see what real workflows look like."
          className="mb-16"
        />

        <div className="grid md:grid-cols-3 gap-6">
          {workflows.map((wf, idx) => (
            <motion.div
              key={wf.title}
              className="relative flex flex-col bg-card border border-border hover:border-opacity-60 rounded-2xl overflow-hidden group"
              style={{ '--wf-color': wf.color } as React.CSSProperties}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              whileHover={{ borderColor: wf.color + '60', y: -4 }}
            >
              {/* Mini graph preview */}
              <div className="relative h-28 overflow-hidden bg-background border-b border-border">
                <div className="absolute inset-0 p-3">
                  <MiniGraph nodes={wf.nodes} edges={wf.edges} />
                </div>
                {/* Gradient overlay */}
                <div className="absolute bottom-0 left-0 right-0 h-8"
                  style={{ background: `linear-gradient(to top, #141428, transparent)` }}
                />
              </div>

              <div className="p-5 flex flex-col gap-3 flex-1">
                {/* Title */}
                <div className="flex items-start gap-2">
                  <div
                    className="w-2 h-5 rounded-sm flex-shrink-0 mt-0.5"
                    style={{ background: wf.color }}
                  />
                  <h3 className="text-base font-bold text-text-primary leading-snug">{wf.title}</h3>
                </div>

                {/* Description */}
                <p className="text-sm text-text-secondary leading-relaxed flex-1">{wf.description}</p>

                {/* Node badges */}
                <div className="flex flex-wrap gap-1.5">
                  {wf.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs font-mono px-2 py-0.5 rounded-md"
                      style={{
                        background: wf.color + '12',
                        color: wf.color + 'bb',
                        border: `1px solid ${wf.color}20`,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA link */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
        >
          <a
            href="/showcase"
            className="inline-flex items-center gap-2 text-primary hover:text-primary/80 font-medium transition-colors"
          >
            View all 6 workflow examples
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>
        </motion.div>
      </div>
    </section>
  )
}
