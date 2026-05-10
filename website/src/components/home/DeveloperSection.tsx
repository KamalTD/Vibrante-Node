'use client'

import { motion } from 'framer-motion'
import { CodeBlock } from '@/components/ui/CodeBlock'
import { SectionHeader } from '@/components/ui/SectionHeader'

const NODE_EXAMPLE = `from src.nodes.base import BaseNode

class My_Node(BaseNode):
    name = "my_node"

    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("file_path", "string", widget_type="text")
        self.add_input("scale",     "float",  widget_type="float", default=1.0)
        self.add_output("result",   "any")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        path  = inputs.get("file_path", "")
        scale = inputs.get("scale", 1.0)
        # ... your logic here ...
        return {"result": path, "exec_out": True}

def register_node():
    return My_Node`

const JSON_EXAMPLE = `{
  "node_id": "my_node",
  "name":    "my_node",
  "description": "My custom node",
  "category":    "Custom",
  "use_exec":    true,
  "inputs":  [
    { "name": "file_path", "type": "string",
      "widget_type": "text" },
    { "name": "scale",     "type": "float",
      "widget_type": "float", "default": 1.0 }
  ],
  "outputs": [
    { "name": "result", "type": "any" }
  ],
  "python_code": "..."
}`

const features = [
  {
    icon: '📁',
    title: 'Drop-in nodes',
    description: 'Place any .json file in nodes/ folder — it registers automatically on the next startup or script refresh.',
  },
  {
    icon: '⚡',
    title: 'Async first',
    description: 'Every execute() is async. Run Houdini cooks, HTTP calls, file I/O — all without blocking the UI.',
  },
  {
    icon: '🔌',
    title: 'Type-safe ports',
    description: 'String, float, int, bool, list, any. The engine validates connections and shows type-colored pins.',
  },
  {
    icon: '🛠',
    title: 'Node Builder GUI',
    description: 'Press Ctrl+E to open the visual Node Builder. Build nodes without touching JSON — code is generated for you.',
  },
]

export function DeveloperSection() {
  return (
    <section className="py-24 bg-background relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-primary/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Developer Experience"
          title="Build Nodes in"
          titleGradient="Minutes"
          subtitle="Any Python class that inherits BaseNode becomes a live node. The JSON format is simple enough to write by hand — or use the Node Builder GUI."
          className="mb-16"
        />

        <div className="grid lg:grid-cols-2 gap-8 items-start">
          {/* Code examples */}
          <div className="flex flex-col gap-4">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 rounded-full bg-primary" />
                <span className="text-sm font-semibold text-text-primary">Python class (python_code)</span>
              </div>
              <CodeBlock
                code={NODE_EXAMPLE}
                language="python"
                title="my_node.py"
                showLineNumbers={true}
              />
            </div>

            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 rounded-full bg-secondary" />
                <span className="text-sm font-semibold text-text-primary">Node definition (.json)</span>
              </div>
              <CodeBlock
                code={JSON_EXAMPLE}
                language="json"
                title="my_node.json"
                showLineNumbers={true}
              />
            </div>
          </div>

          {/* Right column */}
          <div className="flex flex-col gap-6">
            {/* DX callout */}
            <motion.div
              className="p-6 rounded-2xl bg-card border border-border relative overflow-hidden"
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl" />
              <h3 className="text-lg font-bold text-text-primary mb-2">
                Drop the JSON file in{' '}
                <code className="text-primary bg-primary/10 px-1.5 py-0.5 rounded text-sm">nodes/</code>
              </h3>
              <p className="text-text-secondary text-sm leading-relaxed">
                It appears in the library instantly. No restart required — use{' '}
                <kbd className="text-xs bg-card border border-border px-1.5 py-0.5 rounded font-mono">Scripts → Refresh</kbd>{' '}
                to reload all nodes without closing the app.
              </p>

              <div className="mt-4 flex items-center gap-2 text-sm text-green-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Zero boilerplate — inherit BaseNode, implement execute()
              </div>
            </motion.div>

            {/* Feature list */}
            <div className="grid grid-cols-2 gap-4">
              {features.map((feat, idx) => (
                <motion.div
                  key={feat.title}
                  className="p-4 rounded-xl bg-card border border-border"
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                >
                  <div className="text-xl mb-2">{feat.icon}</div>
                  <h4 className="text-sm font-semibold text-text-primary mb-1">{feat.title}</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">{feat.description}</p>
                </motion.div>
              ))}
            </div>

            {/* Port type legend */}
            <motion.div
              className="p-5 rounded-2xl bg-card border border-border"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.3 }}
            >
              <h4 className="text-sm font-semibold text-text-primary mb-3">Port Type Colors</h4>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { type: 'string', color: '#22d3ee', label: 'string' },
                  { type: 'int', color: '#a78bfa', label: 'int' },
                  { type: 'float', color: '#34d399', label: 'float' },
                  { type: 'bool', color: '#f59e0b', label: 'bool' },
                  { type: 'list', color: '#f97316', label: 'list' },
                  { type: 'any', color: '#6b7280', label: 'any' },
                ].map((pt) => (
                  <div key={pt.type} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ background: pt.color }}
                    />
                    <span className="text-xs font-mono text-text-secondary">{pt.label}</span>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-white/60 flex-shrink-0" />
                <span className="text-xs font-mono text-text-secondary">exec (white square)</span>
              </div>
            </motion.div>

            {/* CTA */}
            <div className="flex gap-3">
              <a
                href="/developers"
                className="flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-colors hover:shadow-glow-purple"
              >
                Full API Reference
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
              <a
                href="/docs"
                className="flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold text-primary border border-primary/30 hover:border-primary/60 rounded-xl transition-colors"
              >
                Docs Home
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
