'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'

const docSections = [
  {
    id: 'introduction',
    title: 'Introduction',
    icon: '📖',
    summary: 'What Vibrante-Node is, what problems it solves, and how the node + exec-pin model works.',
    items: ['What is Vibrante-Node?', 'Core concepts: nodes, pins, wires', 'Exec flow vs data flow', 'When to use Vibrante-Node'],
  },
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: '🚀',
    summary: 'Installation from source, first launch, configuring Houdini integration, and running your first workflow.',
    items: ['Requirements (Python 3.10+, PyQt5)', 'Installation from source', 'First launch walkthrough', 'Houdini package setup'],
  },
  {
    id: 'user-guide',
    title: 'User Guide',
    icon: '🎮',
    summary: 'Full guide to the Vibrante-Node UI: canvas, library, log panel, mini-map, canvas search, and keyboard shortcuts.',
    items: ['Canvas navigation', 'Node library', 'Connecting nodes', 'Execution log', 'Mini-map (Ctrl+M)', 'Canvas Search (Ctrl+F)', 'Keyboard shortcuts'],
  },
  {
    id: 'workflow-tutorials',
    title: 'Workflow Tutorials',
    icon: '🎬',
    summary: 'Step-by-step tutorials for building real pipelines: Houdini, Maya, Prism, and AI orchestration workflows.',
    items: ['Houdini geometry workflow', 'Maya batch export', 'Prism asset publishing', 'AI feedback processing', 'Multi-shot rendering'],
  },
  {
    id: 'node-development',
    title: 'Node Development',
    icon: '🔧',
    summary: 'How to create custom nodes: BaseNode API, JSON format, exec pins, port types, and the Node Builder GUI.',
    items: ['BaseNode class reference', 'JSON node format', 'Port types and widgets', 'execute() return values', 'Node Builder GUI (Ctrl+E)', 'Registering and loading nodes'],
  },
  {
    id: 'backend-architecture',
    title: 'Backend Architecture',
    icon: '⚙️',
    summary: 'How the async execution engine works: DAG resolution, signal flow, asyncio integration, and error handling.',
    items: ['NetworkExecutor', 'Async DAG execution', 'Signal/slot model', 'Error propagation', 'GroupNode execution', 'Headless mode'],
  },
  {
    id: 'frontend-architecture',
    title: 'Frontend Architecture',
    icon: '🎨',
    summary: 'The PyQt5 UI: scene graph, NodeWidget, Edge/wire rendering, live wire inspector, mini-map, and theming.',
    items: ['NodeScene / NodeView', 'NodeWidget rendering', 'Edge and port drawing', 'Live Wire Inspector', 'Mini-map (MiniMap)', 'Dark/Light theming'],
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    icon: '📚',
    summary: 'Complete API for BaseNode, HouBridge, PrismCore resolver, WorkflowModel, and all built-in utility functions.',
    items: ['BaseNode API', 'HouBridge 18 methods', 'resolve_prism_core()', 'WorkflowModel schema', 'NodeRegistry', 'ConfigManager'],
  },
  {
    id: 'advanced-topics',
    title: 'Advanced Topics',
    icon: '🔬',
    summary: 'GroupNode subgraphs, autosave/crash recovery, headless execution, workflow serialization, and the Houdini plugin architecture.',
    items: ['GroupNode / Subgraph (Ctrl+Shift+G)', 'Autosave & crash recovery', 'Headless workflow execution', 'Workflow JSON serialization', 'Houdini plugin architecture', 'Environment variables'],
  },
  {
    id: 'contribution',
    title: 'Contribution Guide',
    icon: '🤝',
    summary: 'How to contribute: code style, testing, PR process, and adding new node categories or integrations.',
    items: ['Code style (PEP 8)', 'Writing tests', 'PR process', 'Adding new nodes', 'Adding new DCC integrations', 'Documentation standards'],
  },
  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    icon: '🔍',
    summary: 'Common issues: Houdini connection failures, port bind errors, QScintilla missing, PyQt5 conflicts, and crash recovery.',
    items: ['Houdini bridge not connecting', 'Port already in use', 'QScintilla not installed', 'PyQt5 / PySide2 conflict', 'Reading crash.log', 'Environment variable checklist'],
  },
  {
    id: 'examples',
    title: 'Examples Library',
    icon: '📁',
    summary: 'Ready-to-use .vnw workflow files and custom node examples covering all integration categories.',
    items: ['Houdini examples', 'Maya batch examples', 'Prism workflow examples', 'AI orchestration examples', 'Custom node examples', 'Test workflows'],
  },
  {
    id: 'general-automation',
    title: 'General-Purpose Automation',
    icon: '🤖',
    summary: 'Using Vibrante-Node outside of DCC tools: file operations, HTTP APIs, JSON processing, and Python scripting nodes.',
    items: ['File I/O nodes', 'HTTP request node', 'JSON parse/format', 'ForEach and WhileLoop', 'SetVariable/GetVariable', 'Console Print and logging'],
  },
  {
    id: 'custom-nodes-api',
    title: 'Custom Nodes API',
    icon: '🧩',
    summary: 'The complete custom node API: all add_input() / add_output() options, log_error(), set_output(), parameters dict, and the Node Builder.',
    items: ['add_input() signature', 'add_output() signature', 'log_error() / log_warning()', 'set_output() for GroupOutNode', 'self.parameters dict', 'register_node() contract'],
  },
]

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('introduction')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredSections = docSections.filter(
    (s) =>
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.items.some((item) => item.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const active = docSections.find((s) => s.id === activeSection) ?? docSections[0]

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
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left text-sm transition-all duration-150 ${
                      activeSection === section.id
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
                    }`}
                  >
                    <span className="text-base">{section.icon}</span>
                    <span className="truncate">{section.title}</span>
                    {activeSection === section.id && (
                      <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                    )}
                  </button>
                ))}
              </nav>

              {filteredSections.length === 0 && (
                <p className="text-sm text-text-secondary text-center py-8">
                  No results for "{searchQuery}"
                </p>
              )}
            </aside>

            {/* Main content */}
            <main className="lg:col-span-3 pt-8 pb-16 lg:pl-10">
              <motion.div
                key={activeSection}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
              >
                {/* Breadcrumb */}
                <div className="flex items-center gap-2 text-xs text-text-secondary mb-6">
                  <span>Docs</span>
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="text-text-primary">{active.title}</span>
                </div>

                {/* Title */}
                <div className="flex items-center gap-4 mb-6">
                  <span className="text-4xl">{active.icon}</span>
                  <div>
                    <h1 className="text-3xl font-bold text-text-primary">{active.title}</h1>
                    <p className="text-text-secondary mt-1">{active.summary}</p>
                  </div>
                </div>

                {/* Divider */}
                <div className="border-t border-border mb-8" />

                {/* Overview callout */}
                <div className="p-5 rounded-2xl bg-primary/5 border border-primary/20 mb-8">
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <p className="text-sm font-semibold text-primary mb-1">Documentation in Progress</p>
                      <p className="text-sm text-text-secondary">
                        The full documentation lives in the{' '}
                        <code className="text-xs bg-white/10 px-1.5 py-0.5 rounded font-mono">docs_src/</code> folder of the repository.
                        This index shows the structure and topics covered. Refer to the source files for complete content.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Topics covered */}
                <h2 className="text-lg font-bold text-text-primary mb-4">Topics Covered</h2>
                <div className="grid sm:grid-cols-2 gap-3 mb-10">
                  {active.items.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-3 p-3 rounded-xl bg-card border border-border"
                    >
                      <div className="w-5 h-5 rounded-md bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <svg className="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                      <span className="text-sm text-text-secondary">{item}</span>
                    </div>
                  ))}
                </div>

                {/* All docs sections quick nav */}
                <h2 className="text-lg font-bold text-text-primary mb-4">All Documentation Sections</h2>
                <div className="grid sm:grid-cols-2 gap-3">
                  {docSections.map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`flex items-start gap-3 p-4 rounded-xl border text-left transition-all ${
                        activeSection === section.id
                          ? 'bg-primary/10 border-primary/30'
                          : 'bg-card border-border hover:border-primary/20 hover:bg-card'
                      }`}
                    >
                      <span className="text-2xl flex-shrink-0">{section.icon}</span>
                      <div>
                        <p className="text-sm font-semibold text-text-primary">{section.title}</p>
                        <p className="text-xs text-text-secondary mt-0.5 line-clamp-2">{section.summary}</p>
                      </div>
                    </button>
                  ))}
                </div>

                {/* GitHub link */}
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
              </motion.div>
            </main>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
