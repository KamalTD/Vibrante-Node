'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/Badge'

interface WorkflowNode {
  label: string
  category: string
  color: string
}

interface WorkflowCardProps {
  title: string
  description: string
  nodes: WorkflowNode[]
  tags: string[]
  color: string
  badge: string
  index: number
  steps: string[]
}

type BadgeVariant = 'default' | 'primary' | 'secondary' | 'houdini' | 'maya' | 'blender' | 'prism' | 'deadline' | 'success' | 'warning'

const CATEGORY_BADGE: Record<string, BadgeVariant> = {
  Houdini: 'houdini',
  Maya: 'maya',
  Blender: 'blender',
  Prism: 'prism',
  Deadline: 'deadline',
  Logic: 'primary',
  Script: 'secondary',
  Output: 'success',
  Custom: 'default',
}

function MiniFlowGraph({ nodes, color }: { nodes: WorkflowNode[]; color: string }) {
  const NODE_W = 90
  const NODE_H = 28
  const GAP = 24
  const TOTAL_W = nodes.length * NODE_W + (nodes.length - 1) * GAP
  const SVG_W = Math.max(TOTAL_W + 40, 400)
  const SVG_H = 70

  return (
    <svg
      viewBox={`0 0 ${SVG_W} ${SVG_H}`}
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full"
    >
      <rect width={SVG_W} height={SVG_H} fill="#0a0a0f" rx="8" />
      <pattern id={`g-${color.replace('#', '')}`} width="12" height="12" patternUnits="userSpaceOnUse">
        <path d="M 12 0 L 0 0 0 12" fill="none" stroke="#1e1e3a" strokeWidth="0.3" />
      </pattern>
      <rect width={SVG_W} height={SVG_H} rx="8" fill={`url(#g-${color.replace('#', '')})`} />

      {nodes.map((node, idx) => {
        const nx = 20 + idx * (NODE_W + GAP)
        const ny = (SVG_H - NODE_H) / 2
        const nc = node.color

        return (
          <g key={idx}>
            {/* Wire to next */}
            {idx < nodes.length - 1 && (
              <path
                d={`M ${nx + NODE_W + 3} ${ny + NODE_H / 2} L ${nx + NODE_W + GAP - 3} ${ny + NODE_H / 2}`}
                stroke="#2a2a4a"
                strokeWidth="1.5"
                strokeDasharray="4 3"
                fill="none"
              />
            )}
            {/* Node body */}
            <rect
              x={nx}
              y={ny}
              width={NODE_W}
              height={NODE_H}
              rx="5"
              fill="#141428"
              stroke={nc}
              strokeWidth="0.8"
              strokeOpacity="0.5"
            />
            {/* Left color bar */}
            <rect x={nx} y={ny} width="2.5" height={NODE_H} rx="2.5" fill={nc} opacity="0.8" />
            {/* Exec in */}
            <rect x={nx - 4} y={ny + NODE_H / 2 - 3} width="5" height="5" rx="1" fill="#3a3a5a" />
            {/* Exec out */}
            <rect x={nx + NODE_W - 1} y={ny + NODE_H / 2 - 3} width="5" height="5" rx="1" fill="#3a3a5a" />
            {/* Label */}
            <text
              x={nx + NODE_W / 2}
              y={ny + NODE_H / 2 + 4}
              textAnchor="middle"
              fontSize="7"
              fontFamily="'JetBrains Mono', monospace"
              fill="#c5c5d2"
            >
              {node.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

export function WorkflowCard({
  title,
  description,
  nodes,
  tags,
  color,
  badge,
  index,
  steps,
}: WorkflowCardProps) {
  return (
    <motion.div
      className="flex flex-col bg-card border border-border rounded-2xl overflow-hidden group hover:border-opacity-60 transition-all duration-300"
      style={{ '--card-color': color } as React.CSSProperties}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -6, borderColor: color + '50' }}
    >
      {/* Top color strip */}
      <div className="h-1" style={{ background: color }} />

      {/* Mini flow graph */}
      <div className="h-20 bg-background border-b border-border overflow-hidden p-2">
        <MiniFlowGraph nodes={nodes} color={color} />
      </div>

      <div className="p-6 flex flex-col gap-4 flex-1">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-lg font-bold text-text-primary leading-snug">{title}</h3>
          <span
            className="flex-shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full"
            style={{ background: color + '18', color, border: `1px solid ${color}30` }}
          >
            {badge}
          </span>
        </div>

        {/* Description */}
        <p className="text-sm text-text-secondary leading-relaxed">{description}</p>

        {/* Steps */}
        <div className="flex flex-col gap-2">
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Workflow Steps</p>
          <ol className="flex flex-col gap-1.5">
            {steps.map((step, sIdx) => (
              <li key={sIdx} className="flex items-start gap-2.5 text-sm text-text-secondary">
                <span
                  className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mt-0.5"
                  style={{ background: color + '20', color }}
                >
                  {sIdx + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
        </div>

        {/* Node tags */}
        <div className="flex flex-wrap gap-1.5 mt-auto pt-3 border-t border-border">
          {tags.map((tag) => (
            <Badge
              key={tag}
              variant={CATEGORY_BADGE[nodes.find((n) => n.label.toLowerCase().includes(tag.split('_')[0]))?.category ?? 'Logic'] ?? 'default'}
              className="text-xs font-mono"
            >
              {tag}
            </Badge>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
