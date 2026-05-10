'use client'

import { motion } from 'framer-motion'
import { SectionHeader } from '@/components/ui/SectionHeader'

const integrations = [
  {
    name: 'Houdini',
    description: 'Live TCP JSON-RPC bridge to running Houdini session. Create nodes, set parms, cook, save .hip — all in real-time.',
    color: '#ff6b35',
    bgColor: 'bg-houdini/5',
    borderColor: 'border-houdini/20 hover:border-houdini/50',
    textColor: 'text-houdini',
    badge: 'Live Bridge',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 40 40" fill="none">
        <rect x="4" y="4" width="32" height="32" rx="6" fill="#ff6b35" fillOpacity="0.15" />
        <path d="M10 30V10h4v8h12V10h4v20h-4V22H14v8z" fill="#ff6b35" />
      </svg>
    ),
    features: ['create_node()', 'set_parm()', 'cook_node()', 'run_code()', 'scene_info()'],
  },
  {
    name: 'Maya',
    description: 'Headless action-list pattern using mayapy subprocess. Build full render + publish pipelines without opening the UI.',
    color: '#00aeef',
    bgColor: 'bg-maya/5',
    borderColor: 'border-maya/20 hover:border-maya/50',
    textColor: 'text-maya',
    badge: 'Headless',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 40 40" fill="none">
        <rect x="4" y="4" width="32" height="32" rx="6" fill="#00aeef" fillOpacity="0.15" />
        <path d="M10 10h5l5 12 5-12h5v20h-4V18l-6 12-6-12v12H10z" fill="#00aeef" />
      </svg>
    ),
    features: ['open_scene', 'export_alembic', 'set_frame_range', 'render_sequence', 'batch_mode'],
  },
  {
    name: 'Blender',
    description: 'Headless action-list pattern via Blender background subprocess. Automate modeling, rendering, and export tasks.',
    color: '#ea7600',
    bgColor: 'bg-blender/5',
    borderColor: 'border-blender/20 hover:border-blender/50',
    textColor: 'text-blender',
    badge: 'Headless',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 40 40" fill="none">
        <rect x="4" y="4" width="32" height="32" rx="6" fill="#ea7600" fillOpacity="0.15" />
        <circle cx="20" cy="20" r="8" stroke="#ea7600" strokeWidth="2.5" />
        <circle cx="20" cy="20" r="3" fill="#ea7600" />
        <path d="M10 20h4M26 20h4M20 10v4M20 26v4" stroke="#ea7600" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
    features: ['open_blend', 'render_frame', 'export_gltf', 'apply_modifier', 'python_script'],
  },
  {
    name: 'Prism Pipeline',
    description: '60+ nodes covering the full Prism API. Assets, shots, versions, publishing, USD, and more — all visual.',
    color: '#7c3aed',
    bgColor: 'bg-prism/5',
    borderColor: 'border-prism/20 hover:border-prism/50',
    textColor: 'text-prism',
    badge: '60+ nodes',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 40 40" fill="none">
        <rect x="4" y="4" width="32" height="32" rx="6" fill="#7c3aed" fillOpacity="0.15" />
        <path d="M20 8l10 6v12L20 32 10 26V14z" stroke="#7c3aed" strokeWidth="2" />
        <path d="M20 14l6 3.5v7L20 28l-6-3.5v-7z" fill="#7c3aed" fillOpacity="0.4" />
      </svg>
    ),
    features: ['get_assets()', 'create_version()', 'publish_product()', 'get_shots()', 'usd_export'],
  },
  {
    name: 'Deadline',
    description: 'Submit render jobs for Maya, Houdini, and Blender directly from your workflow. Track status and collect results.',
    color: '#e11d48',
    bgColor: 'bg-deadline/5',
    borderColor: 'border-deadline/20 hover:border-deadline/50',
    textColor: 'text-deadline',
    badge: 'Render Farm',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 40 40" fill="none">
        <rect x="4" y="4" width="32" height="32" rx="6" fill="#e11d48" fillOpacity="0.15" />
        <rect x="10" y="15" width="20" height="3" rx="1.5" fill="#e11d48" />
        <rect x="10" y="21" width="14" height="3" rx="1.5" fill="#e11d48" fillOpacity="0.6" />
        <rect x="10" y="27" width="8" height="3" rx="1.5" fill="#e11d48" fillOpacity="0.3" />
        <circle cx="30" cy="12" r="4" fill="#e11d48" />
        <path d="M28 12l1.5 1.5L33 10" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    features: ['submit_job()', 'get_job_status()', 'cancel_job()', 'get_output_paths()', 'priority'],
  },
  {
    name: 'Python / USD',
    description: 'Drop any Python class in nodes/ and it is live. Full asyncio support. USD workflows via Prism USD integration nodes.',
    color: '#34d399',
    bgColor: 'bg-green-500/5',
    borderColor: 'border-green-500/20 hover:border-green-500/50',
    textColor: 'text-green-400',
    badge: 'Extensible',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 40 40" fill="none">
        <rect x="4" y="4" width="32" height="32" rx="6" fill="#34d399" fillOpacity="0.15" />
        <path d="M12 16l8-6 8 6v8l-8 6-8-6z" stroke="#34d399" strokeWidth="2" />
        <path d="M12 16l8 6 8-6M20 22v8" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    features: ['BaseNode', 'async execute()', 'add_input()', 'add_output()', 'log_error()'],
  },
]

export function Integrations() {
  return (
    <section id="integrations" className="py-24 bg-background relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />

      {/* Background accents */}
      <div className="absolute top-1/2 left-0 w-64 h-64 bg-houdini/5 rounded-full blur-[80px]" />
      <div className="absolute top-1/2 right-0 w-64 h-64 bg-prism/5 rounded-full blur-[80px]" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Integrations"
          title="Works With Your"
          titleGradient="Entire Pipeline"
          subtitle="Every major VFX DCC and pipeline tool — connected, automated, and running from a single visual workflow."
          className="mb-16"
        />

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {integrations.map((integ, idx) => (
            <motion.div
              key={integ.name}
              className={`integration-card relative p-6 rounded-2xl bg-card border ${integ.borderColor} group cursor-default`}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {integ.icon}
                  <div>
                    <h3 className="text-base font-bold text-text-primary">{integ.name}</h3>
                    <span
                      className="inline-block text-xs font-medium px-2 py-0.5 rounded-full mt-0.5"
                      style={{
                        background: integ.color + '20',
                        color: integ.color,
                        border: `1px solid ${integ.color}30`,
                      }}
                    >
                      {integ.badge}
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-text-secondary leading-relaxed mb-4">{integ.description}</p>

              {/* API features */}
              <div className="flex flex-wrap gap-1.5">
                {integ.features.map((f) => (
                  <span
                    key={f}
                    className="text-xs font-mono px-2 py-0.5 rounded-md"
                    style={{
                      background: integ.color + '10',
                      color: integ.color + 'cc',
                      border: `1px solid ${integ.color}20`,
                    }}
                  >
                    {f}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
