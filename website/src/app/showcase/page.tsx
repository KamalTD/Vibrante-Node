import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { WorkflowCard } from '@/components/showcase/WorkflowCard'
import { SectionHeader } from '@/components/ui/SectionHeader'

const workflows = [
  {
    title: 'Maya Publishing Workflow',
    description:
      'Open a Maya scene, export Alembic caches, create a Prism product version, and submit a Deadline render job — fully automated with zero manual steps.',
    color: '#00aeef',
    badge: 'Maya · Prism · Deadline',
    nodes: [
      { label: 'Open Scene', category: 'Maya', color: '#00aeef' },
      { label: 'Export Alembic', category: 'Maya', color: '#00aeef' },
      { label: 'Prism Version', category: 'Prism', color: '#7c3aed' },
      { label: 'Submit Job', category: 'Deadline', color: '#e11d48' },
    ],
    tags: ['maya_open_scene', 'maya_export_abc', 'prism_create_version', 'deadline_submit'],
    steps: [
      'Open Maya scene from path input',
      'Run export_alembic action for selected geo',
      'Create new Prism product version with metadata',
      'Submit Deadline render job with correct paths',
      'Log completion with job ID',
    ],
  },
  {
    title: 'Houdini Groom Workflow',
    description:
      'Build a complete Houdini groom network procedurally: create /obj geo, wire SOP nodes, set all parameters, cook, and save the .hip file via the live JSON-RPC bridge.',
    color: '#ff6b35',
    badge: 'Houdini',
    nodes: [
      { label: 'Create Geo', category: 'Houdini', color: '#ff6b35' },
      { label: 'Add SOP Net', category: 'Houdini', color: '#ff6b35' },
      { label: 'Wire Nodes', category: 'Houdini', color: '#ff6b35' },
      { label: 'Set Parms', category: 'Houdini', color: '#ff6b35' },
      { label: 'Cook & Save', category: 'Houdini', color: '#ff6b35' },
    ],
    tags: ['hou_create_node', 'hou_connect_nodes', 'hou_set_parm', 'hou_cook_node', 'hou_save_hip'],
    steps: [
      'Create /obj-level geo container with hou_create_node',
      'Clear default child nodes, add hair/fur SOP network',
      'Wire SOPs together with hou_connect_nodes',
      'Set all parameters via hou_set_parm batch calls',
      'Cook display node and save .hip to output path',
    ],
  },
  {
    title: 'AI Feedback Processing',
    description:
      'Load customer feedback text, classify sentiment via an HTTP API call, generate a response with an LLM, optionally translate, and write the result to a JSON database.',
    color: '#00d4ff',
    badge: 'AI · Automation',
    nodes: [
      { label: 'Load Feedback', category: 'Script', color: '#22d3ee' },
      { label: 'HTTP API', category: 'Script', color: '#22d3ee' },
      { label: 'Classify', category: 'Logic', color: '#a78bfa' },
      { label: 'Generate', category: 'Script', color: '#22d3ee' },
      { label: 'Write DB', category: 'Output', color: '#34d399' },
    ],
    tags: ['read_file', 'http_request', 'if_else', 'json_parse', 'write_file'],
    steps: [
      'Read feedback JSON from input folder',
      'POST to classification API, parse sentiment score',
      'Route via If/Else: positive → generate thank-you, negative → flag',
      'Call LLM API to generate contextual response text',
      'Append result to SQLite database file',
    ],
  },
  {
    title: 'Batch File Renaming',
    description:
      'List a folder of files, iterate with ForEach, normalize filenames using string nodes, perform the rename, and log every result to the console — no Python scripting needed.',
    color: '#34d399',
    badge: 'Automation',
    nodes: [
      { label: 'List Folder', category: 'Script', color: '#34d399' },
      { label: 'ForEach', category: 'Logic', color: '#a78bfa' },
      { label: 'Normalize', category: 'Script', color: '#22d3ee' },
      { label: 'Rename File', category: 'Output', color: '#34d399' },
      { label: 'Console', category: 'Output', color: '#34d399' },
    ],
    tags: ['list_dir', 'for_each', 'string_replace', 'rename_file', 'console_print'],
    steps: [
      'List all files matching a glob pattern in the target folder',
      'ForEach iterates over each file path',
      'String nodes normalize: lowercase, strip spaces, add prefix',
      'Rename each file using the normalized name',
      'Console Print logs: old name → new name with timestamp',
    ],
  },
  {
    title: 'Asset Version Check',
    description:
      'Query Prism for all assets in a project, iterate over each, get the latest published version, compare against a minimum required version, and send a notification if outdated.',
    color: '#7c3aed',
    badge: 'Prism Pipeline',
    nodes: [
      { label: 'Get Assets', category: 'Prism', color: '#7c3aed' },
      { label: 'ForEach', category: 'Logic', color: '#a78bfa' },
      { label: 'Get Version', category: 'Prism', color: '#7c3aed' },
      { label: 'Compare', category: 'Logic', color: '#a78bfa' },
      { label: 'Notify', category: 'Output', color: '#34d399' },
    ],
    tags: ['prism_get_assets', 'for_each', 'prism_get_latest_version', 'if_else', 'console_print'],
    steps: [
      'prism_get_assets fetches all assets for the project',
      'ForEach loops over each asset entry',
      'prism_get_latest_version queries Prism for that asset',
      'Compare version string against minimum required version',
      'If outdated: Console Print warning with asset name + versions',
    ],
  },
  {
    title: 'Multi-Shot Rendering',
    description:
      'Build a shot list from a CSV, iterate over every shot, load its .hip file, set frame ranges from metadata, submit a Mantra/Karma render, and collect all output paths.',
    color: '#e11d48',
    badge: 'Houdini · Deadline',
    nodes: [
      { label: 'Read CSV', category: 'Script', color: '#22d3ee' },
      { label: 'ForEach', category: 'Logic', color: '#a78bfa' },
      { label: 'Load HIP', category: 'Houdini', color: '#ff6b35' },
      { label: 'Set Range', category: 'Houdini', color: '#ff6b35' },
      { label: 'Submit', category: 'Deadline', color: '#e11d48' },
    ],
    tags: ['read_csv', 'for_each', 'hou_open_hip', 'hou_set_frame_range', 'deadline_submit'],
    steps: [
      'Read shot CSV: shot_name, hip_path, start_frame, end_frame',
      'ForEach iterates over every row in the shot list',
      'Open each .hip file via the Houdini bridge',
      'Set playback range with hou_set_frame_range',
      'Submit Deadline job and collect render output paths',
    ],
  },
]

export default function ShowcasePage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-20" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-primary/8 rounded-full blur-[100px]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            badge="Workflow Library"
            title="Real Workflows,"
            titleGradient="Real Results"
            subtitle="Six production-grade workflow patterns — from asset publishing to AI orchestration. Each runs in Vibrante-Node without writing a single script."
            align="center"
          />
        </div>
      </section>

      {/* Workflow grid */}
      <section className="pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Stats bar */}
          <div className="flex flex-wrap gap-6 py-6 mb-12 border-y border-border">
            {[
              { label: 'Workflow Templates', value: '6' },
              { label: 'DCC Integrations', value: '5' },
              { label: 'Built-in Nodes Used', value: '30+' },
              { label: 'Manual Steps', value: '0' },
            ].map((s) => (
              <div key={s.label} className="flex flex-col">
                <span className="text-2xl font-bold text-primary">{s.value}</span>
                <span className="text-sm text-text-secondary">{s.label}</span>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
            {workflows.map((wf, idx) => (
              <WorkflowCard
                key={wf.title}
                {...wf}
                index={idx}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-surface border-t border-border">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-text-primary mb-4">
            Build Your Own Workflow
          </h2>
          <p className="text-text-secondary mb-8">
            These are just starting points. Vibrante-Node gives you 165+ nodes to combine into any automation your pipeline needs.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <a
              href="/docs"
              className="px-7 py-3 text-base font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-colors hover:shadow-glow-purple"
            >
              Get Started
            </a>
            <a
              href="/developers"
              className="px-7 py-3 text-base font-semibold text-primary border border-primary/30 hover:border-primary/60 rounded-xl transition-colors"
            >
              Developer Docs
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
