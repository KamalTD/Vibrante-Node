'use client'

import { useEffect, useRef, useState } from 'react'

// ─── Type definitions ────────────────────────────────────────────────────────

interface NodeDef {
  id: string
  x: number
  y: number
  w: number
  h: number
  title: string
  category: string
  color: string
  execIn?: boolean
  execOut?: boolean
  inputs: PortDef[]
  outputs: PortDef[]
}

interface PortDef {
  name: string
  color: string
  type: 'data' | 'exec'
}

interface Connection {
  fromNode: string
  fromPort: string
  toNode: string
  toPort: string
  isExec: boolean
}

// ─── Node layout ─────────────────────────────────────────────────────────────

const NODE_HEADER = 28
const PORT_ROW = 20
const PORT_RADIUS = 5
const EXEC_SIZE = 7

const NODES: NodeDef[] = [
  {
    id: 'python_script',
    x: 30, y: 80, w: 170, h: 90,
    title: 'Python Script',
    category: 'Script',
    color: '#22d3ee',
    execIn: true, execOut: true,
    inputs: [{ name: 'folder_path', color: '#22d3ee', type: 'data' }],
    outputs: [{ name: 'file_list', color: '#f97316', type: 'data' }],
  },
  {
    id: 'foreach',
    x: 255, y: 60, w: 150, h: 110,
    title: 'ForEach',
    category: 'Logic',
    color: '#a78bfa',
    execIn: true, execOut: true,
    inputs: [{ name: 'items', color: '#f97316', type: 'data' }],
    outputs: [
      { name: 'item', color: '#22d3ee', type: 'data' },
      { name: 'loop_exec', color: '#ffffff', type: 'exec' },
    ],
  },
  {
    id: 'hou_create',
    x: 255, y: 230, w: 180, h: 100,
    title: 'Houdini: Create Node',
    category: 'Houdini',
    color: '#ff6b35',
    execIn: true, execOut: true,
    inputs: [{ name: 'parent_path', color: '#22d3ee', type: 'data' }],
    outputs: [{ name: 'node_path', color: '#22d3ee', type: 'data' }],
  },
  {
    id: 'hou_setparm',
    x: 255, y: 390, w: 180, h: 100,
    title: 'Houdini: Set Parm',
    category: 'Houdini',
    color: '#ff6b35',
    execIn: true, execOut: true,
    inputs: [
      { name: 'node_path', color: '#22d3ee', type: 'data' },
      { name: 'value', color: '#34d399', type: 'data' },
    ],
    outputs: [],
  },
  {
    id: 'hou_cook',
    x: 490, y: 310, w: 170, h: 90,
    title: 'Houdini: Cook Node',
    category: 'Houdini',
    color: '#ff6b35',
    execIn: true, execOut: true,
    inputs: [{ name: 'node_path', color: '#22d3ee', type: 'data' }],
    outputs: [{ name: 'result', color: '#34d399', type: 'data' }],
  },
  {
    id: 'console_print',
    x: 490, y: 80, w: 160, h: 90,
    title: 'Console Print',
    category: 'Output',
    color: '#34d399',
    execIn: true, execOut: true,
    inputs: [{ name: 'message', color: '#22d3ee', type: 'data' }],
    outputs: [],
  },
]

const CONNECTIONS: Connection[] = [
  { fromNode: 'python_script', fromPort: 'exec_out', toNode: 'foreach', toPort: 'exec_in', isExec: true },
  { fromNode: 'python_script', fromPort: 'file_list', toNode: 'foreach', toPort: 'items', isExec: false },
  { fromNode: 'foreach', fromPort: 'loop_exec', toNode: 'hou_create', toPort: 'exec_in', isExec: true },
  { fromNode: 'foreach', fromPort: 'item', toNode: 'hou_create', toPort: 'parent_path', isExec: false },
  { fromNode: 'hou_create', fromPort: 'exec_out', toNode: 'hou_setparm', toPort: 'exec_in', isExec: true },
  { fromNode: 'hou_create', fromPort: 'node_path', toNode: 'hou_setparm', toPort: 'node_path', isExec: false },
  { fromNode: 'hou_setparm', fromPort: 'exec_out', toNode: 'hou_cook', toPort: 'exec_in', isExec: true },
  { fromNode: 'hou_cook', fromPort: 'exec_out', toNode: 'console_print', toPort: 'exec_in', isExec: true },
  { fromNode: 'hou_cook', fromPort: 'result', toNode: 'console_print', toPort: 'message', isExec: false },
]

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getNode(id: string): NodeDef {
  return NODES.find((n) => n.id === id)!
}

// Get port world position
function getPortPos(nodeId: string, portName: string, side: 'left' | 'right') {
  const node = getNode(nodeId)

  if (portName === 'exec_in' || portName === 'exec_out') {
    const px = side === 'left' ? node.x : node.x + node.w
    const py = node.y + NODE_HEADER / 2
    return { x: px, y: py }
  }

  const allPorts = side === 'left' ? node.inputs : node.outputs
  const portIdx = allPorts.findIndex((p) => p.name === portName)
  if (portIdx === -1) return { x: node.x + node.w / 2, y: node.y + node.h / 2 }

  // Skip exec pin row
  const hasExec = side === 'left' ? node.execIn : node.execOut
  const rowStart = NODE_HEADER + (hasExec ? PORT_ROW : 0)
  const px = side === 'left' ? node.x : node.x + node.w
  const py = node.y + rowStart + portIdx * PORT_ROW + PORT_ROW / 2
  return { x: px, y: py }
}

function getConnectionPoints(conn: Connection) {
  const fromNode = getNode(conn.fromNode)
  const toNode = getNode(conn.toNode)

  let from: { x: number; y: number }
  let to: { x: number; y: number }

  if (conn.fromPort === 'exec_out') {
    from = { x: fromNode.x + fromNode.w, y: fromNode.y + NODE_HEADER / 2 }
  } else if (conn.fromPort === 'loop_exec') {
    // loop_exec is an output
    const outIdx = fromNode.outputs.findIndex((p) => p.name === 'loop_exec')
    const hasExec = fromNode.execOut
    const rowStart = NODE_HEADER + (hasExec ? PORT_ROW : 0)
    from = { x: fromNode.x + fromNode.w, y: fromNode.y + rowStart + outIdx * PORT_ROW + PORT_ROW / 2 }
  } else {
    from = getPortPos(conn.fromNode, conn.fromPort, 'right')
  }

  if (conn.toPort === 'exec_in') {
    to = { x: toNode.x, y: toNode.y + NODE_HEADER / 2 }
  } else {
    to = getPortPos(conn.toNode, conn.toPort, 'left')
  }

  return { from, to }
}

function bezierPath(from: { x: number; y: number }, to: { x: number; y: number }) {
  const dx = Math.abs(to.x - from.x) * 0.5
  return `M ${from.x} ${from.y} C ${from.x + dx} ${from.y}, ${to.x - dx} ${to.y}, ${to.x} ${to.y}`
}

// ─── Animation sequence ───────────────────────────────────────────────────────
// 8 second loop. Each step: [node_id, delay_ms, duration_ms]
const SEQUENCE = [
  { nodeId: 'python_script', start: 0, end: 1200 },
  { nodeId: 'foreach', start: 1200, end: 2600 },
  { nodeId: 'hou_create', start: 2600, end: 3800 },
  { nodeId: 'hou_setparm', start: 3800, end: 5000 },
  { nodeId: 'hou_cook', start: 5000, end: 6200 },
  { nodeId: 'console_print', start: 6200, end: 7600 },
]

const LOG_LINES = [
  { text: '> Scanning folder: /assets/geo/', t: 800 },
  { text: '> Found 4 files — starting ForEach loop', t: 1800 },
  { text: '> [Houdini] Created /obj/my_geo (geo)', t: 3200 },
  { text: '> [Houdini] Set parm: fileName = "asset_v003.abc"', t: 4400 },
  { text: '> [Houdini] Cook complete ✓  (0.34s)', t: 5800 },
  { text: '> Pipeline complete — 4/4 files processed', t: 7000 },
]

// ─── Component ────────────────────────────────────────────────────────────────

export function NodeGraphSVG() {
  const [tick, setTick] = useState(0)
  const [elapsedMs, setElapsedMs] = useState(0)
  const startRef = useRef<number>(Date.now())
  const CYCLE = 8200

  useEffect(() => {
    let raf: number
    const animate = () => {
      const now = Date.now()
      const elapsed = (now - startRef.current) % CYCLE
      setElapsedMs(elapsed)
      setTick((t) => t + 1)
      raf = requestAnimationFrame(animate)
    }
    raf = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(raf)
  }, [])

  const activeNodeId = SEQUENCE.find(
    (s) => elapsedMs >= s.start && elapsedMs < s.end
  )?.nodeId ?? null

  const visibleLogs = LOG_LINES.filter((l) => elapsedMs >= l.t)

  const categoryColor: Record<string, string> = {
    Script: '#22d3ee',
    Logic: '#a78bfa',
    Houdini: '#ff6b35',
    Output: '#34d399',
  }

  // Particle progress for each exec connection
  function getParticleT(connIdx: number): number | null {
    // Map connection to the source node activation
    const execConns = CONNECTIONS.filter((c) => c.isExec)
    const execConn = execConns[connIdx]
    if (!execConn) return null
    const step = SEQUENCE.find((s) => s.nodeId === execConn.fromNode)
    if (!step) return null
    const elapsed = elapsedMs - step.start
    const duration = step.end - step.start
    if (elapsed < 0 || elapsed > duration) return null
    return elapsed / duration
  }

  return (
    <div className="relative w-full h-full select-none">
      <svg
        viewBox="0 0 720 560"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
        style={{ fontFamily: "'JetBrains Mono', monospace" }}
      >
        <defs>
          {/* Glow filter purple */}
          <filter id="glow-purple" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="glow-orange" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="glow-cyan" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="glow-green" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          {/* Radial gradient for active node */}
          <radialGradient id="active-orange" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ff6b35" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#ff6b35" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="active-cyan" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="active-purple" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#a78bfa" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="active-green" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#34d399" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#34d399" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Background */}
        <rect x="0" y="0" width="720" height="420" rx="16" fill="#0a0a0f" />

        {/* Grid */}
        <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
          <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#1e1e3a" strokeWidth="0.4" />
        </pattern>
        <rect x="0" y="0" width="720" height="420" rx="16" fill="url(#grid)" opacity="0.6" />

        {/* ── Connections ─────────────────────────────────────────── */}
        {CONNECTIONS.map((conn, idx) => {
          const { from, to } = getConnectionPoints(conn)
          const path = bezierPath(from, to)
          const isActive = conn.fromNode === activeNodeId || conn.toNode === activeNodeId

          if (conn.isExec) {
            return (
              <g key={idx}>
                {/* Static exec wire */}
                <path
                  d={path}
                  fill="none"
                  stroke="#2a2a4a"
                  strokeWidth="2"
                  strokeDasharray="6 4"
                />
                {/* Active exec wire */}
                {isActive && (
                  <path
                    d={path}
                    fill="none"
                    stroke="rgba(255,255,255,0.9)"
                    strokeWidth="2"
                    strokeDasharray="6 4"
                    strokeDashoffset={
                      -((elapsedMs / 40) % 20)
                    }
                    filter="url(#glow-purple)"
                  />
                )}
              </g>
            )
          } else {
            const portColor = conn.isExec ? '#fff' : '#22d3ee'
            return (
              <g key={idx}>
                <path
                  d={path}
                  fill="none"
                  stroke={isActive ? '#22d3ee' : '#1e2a3a'}
                  strokeWidth={isActive ? 1.8 : 1.2}
                  opacity={isActive ? 0.9 : 0.4}
                />
              </g>
            )
          }
        })}

        {/* ── Particle dots on exec wires ─────────────────────────── */}
        {CONNECTIONS.filter((c) => c.isExec).map((conn, idx) => {
          const { from, to } = getConnectionPoints(conn)
          const step = SEQUENCE.find((s) => s.nodeId === conn.fromNode)
          if (!step) return null
          const elapsed = elapsedMs - step.start
          const duration = step.end - step.start
          if (elapsed < 0 || elapsed > duration) return null
          const t = elapsed / duration

          // Lerp along bezier (approximate)
          const dx = Math.abs(to.x - from.x) * 0.5
          const px = cubicBezier(from.x, from.x + dx, to.x - dx, to.x, t)
          const py = cubicBezier(from.y, from.y, to.y, to.y, t)

          return (
            <circle
              key={`particle-${idx}`}
              cx={px}
              cy={py}
              r="4"
              fill="white"
              filter="url(#glow-purple)"
              opacity={Math.min(1, t * 5, (1 - t) * 5)}
            />
          )
        })}

        {/* ── Nodes ───────────────────────────────────────────────── */}
        {NODES.map((node) => {
          const isActive = node.id === activeNodeId
          const catColor = categoryColor[node.category] ?? '#6b7280'
          const glowId =
            node.category === 'Houdini' ? 'glow-orange' :
            node.category === 'Logic' ? 'glow-purple' :
            node.category === 'Script' ? 'glow-cyan' : 'glow-green'

          return (
            <g key={node.id}>
              {/* Glow halo when active */}
              {isActive && (
                <ellipse
                  cx={node.x + node.w / 2}
                  cy={node.y + node.h / 2}
                  rx={node.w / 2 + 20}
                  ry={node.h / 2 + 16}
                  fill={`url(#active-${
                    node.category === 'Houdini' ? 'orange' :
                    node.category === 'Logic' ? 'purple' :
                    node.category === 'Script' ? 'cyan' : 'green'
                  })`}
                />
              )}

              {/* Node body */}
              <rect
                x={node.x}
                y={node.y}
                width={node.w}
                height={node.h}
                rx="8"
                fill="#141428"
                stroke={isActive ? catColor : '#1e1e3a'}
                strokeWidth={isActive ? 1.5 : 1}
                filter={isActive ? `url(#${glowId})` : undefined}
              />

              {/* Header strip */}
              <rect
                x={node.x}
                y={node.y}
                width={node.w}
                height={NODE_HEADER}
                rx="8"
                fill={catColor + '22'}
              />
              <rect
                x={node.x}
                y={node.y + NODE_HEADER - 4}
                width={node.w}
                height="4"
                fill={catColor + '22'}
              />

              {/* Header color bar */}
              <rect
                x={node.x}
                y={node.y}
                width="3"
                height={NODE_HEADER}
                rx="3"
                fill={catColor}
                opacity={isActive ? 1 : 0.6}
              />

              {/* Node title */}
              <text
                x={node.x + 12}
                y={node.y + 18}
                fontSize="10"
                fontWeight="600"
                fill={isActive ? '#ffffff' : '#c5c5d2'}
                letterSpacing="0.3"
              >
                {node.title}
              </text>

              {/* Active indicator dot */}
              {isActive && (
                <circle
                  cx={node.x + node.w - 10}
                  cy={node.y + 14}
                  r="3"
                  fill={catColor}
                  filter={`url(#${glowId})`}
                />
              )}

              {/* ── Exec pins ────── */}
              {node.execIn && (
                <g>
                  <rect
                    x={node.x - EXEC_SIZE / 2}
                    y={node.y + NODE_HEADER / 2 - EXEC_SIZE / 2}
                    width={EXEC_SIZE}
                    height={EXEC_SIZE}
                    rx="1.5"
                    fill={isActive ? '#ffffff' : '#3a3a5a'}
                    stroke={isActive ? '#ffffff' : '#4a4a6a'}
                    strokeWidth="0.5"
                  />
                </g>
              )}
              {node.execOut && (
                <rect
                  x={node.x + node.w - EXEC_SIZE / 2}
                  y={node.y + NODE_HEADER / 2 - EXEC_SIZE / 2}
                  width={EXEC_SIZE}
                  height={EXEC_SIZE}
                  rx="1.5"
                  fill={isActive ? '#ffffff' : '#3a3a5a'}
                  stroke={isActive ? '#ffffff' : '#4a4a6a'}
                  strokeWidth="0.5"
                />
              )}

              {/* ── Input ports ─── */}
              {node.inputs.map((port, pIdx) => {
                const yOff = node.y + NODE_HEADER + (node.execIn ? PORT_ROW : 0) + pIdx * PORT_ROW + PORT_ROW / 2
                return (
                  <g key={`in-${pIdx}`}>
                    <circle
                      cx={node.x}
                      cy={yOff}
                      r={PORT_RADIUS}
                      fill={isActive ? port.color : port.color + '55'}
                      stroke={port.color}
                      strokeWidth="1"
                    />
                    <text
                      x={node.x + PORT_RADIUS + 5}
                      y={yOff + 4}
                      fontSize="8"
                      fill={isActive ? '#d4d4d4' : '#7a7a9a'}
                    >
                      {port.name}
                    </text>
                  </g>
                )
              })}

              {/* ── Output ports ── */}
              {node.outputs.map((port, pIdx) => {
                const yOff = node.y + NODE_HEADER + (node.execOut ? PORT_ROW : 0) + pIdx * PORT_ROW + PORT_ROW / 2
                const isExecPort = port.type === 'exec'
                return (
                  <g key={`out-${pIdx}`}>
                    {isExecPort ? (
                      <rect
                        x={node.x + node.w - EXEC_SIZE / 2}
                        y={yOff - EXEC_SIZE / 2}
                        width={EXEC_SIZE}
                        height={EXEC_SIZE}
                        rx="1.5"
                        fill={isActive ? '#ffffff' : '#3a3a5a'}
                        stroke={isActive ? '#ffffff' : '#4a4a6a'}
                        strokeWidth="0.5"
                      />
                    ) : (
                      <circle
                        cx={node.x + node.w}
                        cy={yOff}
                        r={PORT_RADIUS}
                        fill={isActive ? port.color : port.color + '55'}
                        stroke={port.color}
                        strokeWidth="1"
                      />
                    )}
                    <text
                      x={node.x + node.w - PORT_RADIUS - 5}
                      y={yOff + 4}
                      fontSize="8"
                      fill={isActive ? '#d4d4d4' : '#7a7a9a'}
                      textAnchor="end"
                    >
                      {port.name}
                    </text>
                  </g>
                )
              })}

              {/* Progress bar for cook node */}
              {node.id === 'hou_cook' && activeNodeId === 'hou_cook' && (() => {
                const step = SEQUENCE.find((s) => s.nodeId === 'hou_cook')!
                const t = Math.min(1, (elapsedMs - step.start) / (step.end - step.start))
                return (
                  <g>
                    <rect x={node.x + 8} y={node.y + node.h - 14} width={node.w - 16} height="4" rx="2" fill="#0a0a1a" />
                    <rect x={node.x + 8} y={node.y + node.h - 14} width={(node.w - 16) * t} height="4" rx="2" fill="#ff6b35" />
                  </g>
                )
              })()}
            </g>
          )
        })}

        {/* ── Log Panel ───────────────────────────────────────────── */}
        <rect x="0" y="422" width="720" height="138" rx="0" fill="#0a0a12" />
        <rect x="0" y="422" width="720" height="1" fill="#1e1e3a" />

        {/* Log header */}
        <rect x="0" y="422" width="720" height="22" fill="#0f0f1a" />
        <text x="12" y="436" fontSize="9" fontWeight="600" fill="#5a5a7a" letterSpacing="1">
          EXECUTION LOG
        </text>
        <circle cx="706" cy="433" r="4" fill={activeNodeId ? '#34d399' : '#3a3a5a'} />

        {/* Log lines */}
        {visibleLogs.map((log, idx) => (
          <text
            key={idx}
            x="12"
            y={449 + idx * 16}
            fontSize="9"
            fontFamily="'JetBrains Mono', monospace"
            fill={idx === visibleLogs.length - 1 ? '#c3e88d' : '#546e7a'}
            opacity={idx === visibleLogs.length - 1 ? 1 : 0.7}
          >
            {log.text}
          </text>
        ))}

        {/* Cursor blink */}
        {activeNodeId && (
          <rect
            x={visibleLogs.length > 0 ? 12 + visibleLogs[visibleLogs.length - 1].text.length * 5.4 : 12}
            y={visibleLogs.length > 0 ? 441 + (visibleLogs.length - 1) * 16 : 441}
            width="6"
            height="9"
            fill="#6c63ff"
            opacity={Math.floor(elapsedMs / 500) % 2 === 0 ? 1 : 0}
          />
        )}
      </svg>
    </div>
  )
}

// Cubic Bezier helper (De Casteljau)
function cubicBezier(p0: number, p1: number, p2: number, p3: number, t: number): number {
  const mt = 1 - t
  return mt * mt * mt * p0 + 3 * mt * mt * t * p1 + 3 * mt * t * t * p2 + t * t * t * p3
}
