import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { ApiExample } from '@/components/developers/ApiExample'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Badge } from '@/components/ui/Badge'

const bridgeApi = [
  { method: 'bridge.ping()', returns: '{"status": "ok", "version": "..."}', desc: 'Check connection to Houdini' },
  { method: 'bridge.create_node(parent, type, name)', returns: '{"path": "/obj/geo1", ...}', desc: 'Create a Houdini node' },
  { method: 'bridge.delete_node(path)', returns: '{"deleted": "/obj/geo1"}', desc: 'Delete a node by path' },
  { method: 'bridge.set_parm(node, parm, value)', returns: '{"set": True}', desc: 'Set a single parameter' },
  { method: 'bridge.set_parms(node, parms_dict)', returns: '{"set": True, "count": N}', desc: 'Set multiple parameters at once' },
  { method: 'bridge.get_parm(node, parm)', returns: '{"value": <current>}', desc: 'Read a parameter value' },
  { method: 'bridge.connect_nodes(from, to, out=0, in=0)', returns: '{"connected": True}', desc: 'Wire two nodes together' },
  { method: 'bridge.cook_node(path, force=False)', returns: '{"cooked": True}', desc: 'Cook a node network' },
  { method: 'bridge.run_code(code)', returns: '{"result": <value>}', desc: 'Execute Python code inside Houdini' },
  { method: 'bridge.node_info(path)', returns: '{"path", "type", "category", "children", ...}', desc: 'Get detailed node info' },
  { method: 'bridge.children(path)', returns: '[{"name", "type", "path"}, ...]', desc: 'List child nodes' },
  { method: 'bridge.node_exists(path)', returns: '{"exists": bool}', desc: 'Check if a node path exists' },
  { method: 'bridge.set_display_flag(path, on=True)', returns: '{"set": True}', desc: 'Set display flag on a SOP' },
  { method: 'bridge.save_hip(path="")', returns: '{"saved": "/path/to.hip"}', desc: 'Save the Houdini scene' },
  { method: 'bridge.scene_info()', returns: '{"hip_file", "fps", "frame", "frame_range", ...}', desc: 'Get scene metadata' },
  { method: 'bridge.set_expression(node, parm, expr, lang)', returns: '{"set": True}', desc: 'Set HScript or Python expression' },
  { method: 'bridge.set_frame(frame)', returns: '{"frame": N}', desc: 'Jump to a specific frame' },
  { method: 'bridge.layout_children(path)', returns: '{"done": True}', desc: 'Auto-layout child nodes' },
]

export default function DevelopersPage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-primary/8 rounded-full blur-[100px]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Developer Docs"
            title="Build Nodes."
            titleGradient="Ship Pipelines."
            subtitle="The complete API reference for extending Vibrante-Node. From custom BaseNode classes to the Houdini bridge, action-list pattern, and headless execution."
            align="center"
          />

          <div className="flex flex-wrap justify-center gap-3 mt-8">
            {[
              { label: 'Custom Nodes', href: '#api' },
              { label: 'Houdini Bridge', href: '#houdini-api' },
              { label: 'Maya Headless', href: '#api' },
              { label: 'Prism Integration', href: '#api' },
              { label: 'Headless Execution', href: '#api' },
            ].map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="px-4 py-2 text-sm font-medium text-text-secondary bg-card border border-border hover:border-primary/30 hover:text-text-primary rounded-xl transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Code examples */}
      <ApiExample />

      {/* Houdini Bridge API table */}
      <section id="houdini-api" className="py-24 bg-surface relative">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Houdini Bridge"
            title="Full Bridge"
            titleGradient="API Reference"
            subtitle="All 18 methods available on the HouBridge singleton. Every call goes over TCP JSON-RPC to your live Houdini session."
            align="left"
            className="mb-10"
          />

          <div className="rounded-2xl overflow-hidden border border-border bg-card">
            {/* Table header */}
            <div className="grid grid-cols-12 px-4 py-3 bg-surface border-b border-border">
              <div className="col-span-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">Method</div>
              <div className="col-span-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Returns</div>
              <div className="col-span-5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Description</div>
            </div>

            {/* Table rows */}
            {bridgeApi.map((row, idx) => (
              <div
                key={idx}
                className={`grid grid-cols-12 px-4 py-3 border-b border-border/50 hover:bg-white/2 transition-colors ${
                  idx === bridgeApi.length - 1 ? 'border-0' : ''
                }`}
              >
                <div className="col-span-4 pr-4">
                  <code className="text-xs font-mono text-houdini">{row.method}</code>
                </div>
                <div className="col-span-3 pr-4">
                  <code className="text-xs font-mono text-green-400/80">{row.returns}</code>
                </div>
                <div className="col-span-5">
                  <span className="text-sm text-text-secondary">{row.desc}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Usage note */}
          <div className="mt-6 p-4 rounded-xl bg-houdini/5 border border-houdini/20 flex gap-3">
            <svg className="w-5 h-5 text-houdini flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-text-secondary">
              <strong className="text-houdini">Import:</strong>{' '}
              <code className="font-mono text-xs bg-houdini/10 px-1.5 py-0.5 rounded">from src.utils.hou_bridge import get_bridge</code>.
              Never import <code className="font-mono text-xs">hou</code> directly. Never call{' '}
              <code className="font-mono text-xs">hou_bridge.get_hou()</code> — that function does not exist.
            </div>
          </div>
        </div>
      </section>

      {/* Node JSON format */}
      <section className="py-24 bg-background relative">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Node Format"
            title="The .json"
            titleGradient="Node Schema"
            subtitle="Every node is defined by a single JSON file. Drop it in nodes/ — no plugin system, no registration, no restart required."
            align="left"
            className="mb-10"
          />

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Port type table */}
            <div className="rounded-2xl overflow-hidden border border-border bg-card">
              <div className="px-5 py-4 border-b border-border bg-surface">
                <h3 className="text-sm font-semibold text-text-primary">Port Types</h3>
              </div>
              <div className="p-2">
                {[
                  { type: 'string', widget: 'text', color: '#22d3ee', note: 'Text input widget' },
                  { type: 'float', widget: 'float', color: '#34d399', note: 'Numeric float widget' },
                  { type: 'int', widget: 'int', color: '#a78bfa', note: 'Numeric integer widget' },
                  { type: 'bool', widget: 'checkbox', color: '#f59e0b', note: 'Checkbox widget' },
                  { type: 'list', widget: 'null', color: '#f97316', note: 'List/array data' },
                  { type: 'any', widget: 'null', color: '#6b7280', note: 'Generic exec/data port' },
                ].map((pt) => (
                  <div key={pt.type} className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/3 transition-colors">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: pt.color }} />
                    <code className="text-sm font-mono text-text-primary w-16">{pt.type}</code>
                    <code className="text-sm font-mono text-text-secondary w-24">{pt.widget}</code>
                    <span className="text-sm text-text-secondary">{pt.note}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Exec pin info */}
            <div className="flex flex-col gap-4">
              <div className="p-5 rounded-2xl bg-card border border-border">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-sm bg-white/60" />
                  <h4 className="text-sm font-semibold text-text-primary">Exec Pins (white squares)</h4>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed">
                  Set <code className="font-mono text-xs bg-primary/10 text-primary px-1 rounded">use_exec: true</code> to add exec flow. Always include{' '}
                  <code className="font-mono text-xs bg-white/10 text-text-primary px-1 rounded">exec_in</code> and{' '}
                  <code className="font-mono text-xs bg-white/10 text-text-primary px-1 rounded">exec_out</code> in the JSON arrays. In Python,{' '}
                  <code className="font-mono text-xs bg-white/10 text-text-primary px-1 rounded">super().__init__()</code> adds them automatically — do not add them manually.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-card border border-border">
                <h4 className="text-sm font-semibold text-text-primary mb-3">Categories</h4>
                <div className="flex flex-wrap gap-2">
                  {[
                    { name: 'Houdini', color: '#ff6b35' },
                    { name: 'Maya', color: '#00aeef' },
                    { name: 'Blender', color: '#ea7600' },
                    { name: 'Prism', color: '#7c3aed' },
                    { name: 'Logic', color: '#a78bfa' },
                    { name: 'Math', color: '#34d399' },
                    { name: 'String', color: '#22d3ee' },
                    { name: 'File I/O', color: '#f59e0b' },
                    { name: 'Custom', color: '#6b7280' },
                  ].map((cat) => (
                    <span
                      key={cat.name}
                      className="text-xs font-medium px-2.5 py-1 rounded-full"
                      style={{
                        background: cat.color + '18',
                        color: cat.color,
                        border: `1px solid ${cat.color}30`,
                      }}
                    >
                      {cat.name}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-card border border-border">
                <h4 className="text-sm font-semibold text-text-primary mb-3">Common Mistakes to Avoid</h4>
                <div className="flex flex-col gap-2">
                  {[
                    { wrong: 'hou.node("/obj").createNode(...)', right: 'bridge.create_node("/obj", ...)' },
                    { wrong: 'result = bridge.create_node(...); result.path()', right: 'result = bridge.create_node(...); path = result["path"]' },
                    { wrong: 'Adding exec_in/exec_out manually', right: 'super().__init__() adds them automatically' },
                    { wrong: 'Adding ports twice (in AUTO block + below)', right: 'Add each port exactly once' },
                  ].map((m, i) => (
                    <div key={i} className="text-xs">
                      <div className="flex items-start gap-1.5 text-red-400/80">
                        <svg className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        <code className="font-mono">{m.wrong}</code>
                      </div>
                      <div className="flex items-start gap-1.5 text-green-400/80 mt-0.5">
                        <svg className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <code className="font-mono">{m.right}</code>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
