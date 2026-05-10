import type { Metadata } from 'next'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'

export const metadata: Metadata = {
  title: 'License Agreement — Vibrante-Node',
  description:
    'Vibrante-Node open-core licensing: AGPLv3 runtime, MIT SDK, CC BY 4.0 documentation, and commercial license for studio deployments.',
}

const licenseTable = [
  {
    component: 'Core Runtime',
    license: 'AGPLv3',
    href: 'https://www.gnu.org/licenses/agpl-3.0.en.html',
    free: true,
    badge: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
  },
  {
    component: 'SDK / Public API',
    license: 'MIT',
    href: 'https://opensource.org/licenses/MIT',
    free: true,
    badge: 'bg-sky-500/15 text-sky-400 border-sky-500/25',
  },
  {
    component: 'Documentation & Examples',
    license: 'CC BY 4.0',
    href: 'https://creativecommons.org/licenses/by/4.0/',
    free: true,
    badge: 'bg-violet-500/15 text-violet-400 border-violet-500/25',
  },
  {
    component: 'Official Plugins & Nodes',
    license: 'Commercial',
    href: 'https://github.com/KamalTD/Vibrante-Node/blob/main/COMMERCIAL_LICENSE.md',
    free: false,
    badge: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
  },
  {
    component: 'Enterprise Integrations',
    license: 'Commercial',
    href: 'https://github.com/KamalTD/Vibrante-Node/blob/main/COMMERCIAL_LICENSE.md',
    free: false,
    badge: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
  },
]

const faq = [
  {
    q: 'Can I use Vibrante-Node for personal projects?',
    a: 'Yes. Individual use — whether for personal projects, portfolio work, or skill development — is free under the AGPLv3.',
  },
  {
    q: 'Can I use it at a commercial studio without paying?',
    a: 'Studio pipeline deployment — including multi-seat installations, render farm automation, and client production work — requires a commercial license.',
  },
  {
    q: 'Does the AGPLv3 require me to open-source my pipeline?',
    a: 'If you run a modified version of the core runtime as a networked service and let others interact with it, you must publish your modifications. Private internal use without network distribution does not trigger this obligation.',
  },
  {
    q: 'Can I build closed-source nodes with the SDK?',
    a: 'Yes. The SDK (BaseNode, public node API) is licensed under MIT, which allows building proprietary nodes and integrations without publishing source. Distributing those nodes commercially requires a commercial license.',
  },
  {
    q: 'How do I become a contributor?',
    a: 'Submit a pull request. By doing so you automatically accept the CLA, which lets the project dual-license your contribution while you retain copyright ownership.',
  },
  {
    q: 'Can I use the Vibrante-Node name in my plugin?',
    a: 'Yes, with the form "[YourPlugin] for Vibrante-Node". You may not use "Vibrante-Node [Anything]" as it implies official origin. See the Trademark Policy for details.',
  },
]

function SectionHeader({ label, title, sub }: { label: string; title: string; sub?: string }) {
  return (
    <div className="mb-8">
      <span className="inline-flex items-center px-3 py-1 text-xs font-semibold text-primary bg-primary/10 border border-primary/20 rounded-full mb-4">
        {label}
      </span>
      <h2 className="text-2xl sm:text-3xl font-bold text-text-primary mb-2">{title}</h2>
      {sub && <p className="text-text-secondary">{sub}</p>}
    </div>
  )
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl bg-card border border-border p-6 ${className}`}>
      {children}
    </div>
  )
}

export default function LicensePage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-30 pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-primary/8 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-primary bg-primary/10 border border-primary/20 rounded-full mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            Open-Core Licensing
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-text-primary tracking-tight mb-6">
            License{' '}
            <span className="gradient-text">Agreement</span>
          </h1>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed">
            Vibrante-Node uses an open-core model — the runtime and SDK are open source,
            enterprise components and official plugins require a commercial license.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
            <a
              href="https://github.com/KamalTD/Vibrante-Node/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-all hover:-translate-y-0.5"
            >
              View on GitHub
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
            <a
              href="mailto:m.kamalvfx@gmail.com"
              className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-primary border border-primary/40 hover:border-primary hover:bg-primary/5 rounded-xl transition-all"
            >
              Commercial Inquiry
            </a>
          </div>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-24 space-y-20">

        {/* ── Licensing Overview ───────────────────────────────── */}
        <section id="overview">
          <SectionHeader
            label="Overview"
            title="License Comparison"
            sub="Different components of Vibrante-Node are governed by different licenses."
          />
          <div className="overflow-x-auto rounded-2xl border border-border">
            <table className="w-full text-sm">
              <thead className="bg-surface border-b border-border">
                <tr>
                  <th className="px-5 py-4 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">Component</th>
                  <th className="px-5 py-4 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">License</th>
                  <th className="px-5 py-4 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">Free Use</th>
                  <th className="px-5 py-4 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">Commercial</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {licenseTable.map((row) => (
                  <tr key={row.component} className="hover:bg-white/2 transition-colors">
                    <td className="px-5 py-4 font-medium text-text-primary">{row.component}</td>
                    <td className="px-5 py-4">
                      <a
                        href={row.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`inline-flex items-center px-2.5 py-0.5 text-xs font-semibold rounded-full border ${row.badge} hover:opacity-80 transition-opacity`}
                      >
                        {row.license}
                      </a>
                    </td>
                    <td className="px-5 py-4">
                      {row.free ? (
                        <span className="flex items-center gap-1.5 text-emerald-400 text-xs font-medium">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Free
                        </span>
                      ) : (
                        <span className="text-xs text-text-secondary">See commercial terms</span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      {row.free ? (
                        <span className="text-xs text-text-secondary">AGPLv3 / MIT terms apply</span>
                      ) : (
                        <span className="flex items-center gap-1.5 text-amber-400 text-xs font-medium">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          License required
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── Open-Core Model ──────────────────────────────────── */}
        <section id="open-core">
          <SectionHeader
            label="Model"
            title="Open-Core Architecture"
            sub="The foundation is free and open. Enterprise features are commercial."
          />
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              {
                icon: '🟢',
                title: 'Free Forever',
                items: ['Individuals', 'Students & educators', 'Academic research', 'Open productions', 'OSS contributors'],
              },
              {
                icon: '💼',
                title: 'Commercial License',
                items: ['Studio pipeline deployments', 'Client production work', 'SaaS / cloud hosting', 'Proprietary node packs', 'Render farm integration'],
              },
              {
                icon: '🏢',
                title: 'Enterprise',
                items: ['Multi-studio deployment', 'OEM / product embedding', 'Priority support', 'Custom integrations', 'Negotiated SLA'],
              },
            ].map((col) => (
              <Card key={col.title}>
                <div className="text-2xl mb-3">{col.icon}</div>
                <h3 className="text-sm font-bold text-text-primary mb-3">{col.title}</h3>
                <ul className="space-y-2">
                  {col.items.map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-text-secondary">
                      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary/60 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </section>

        {/* ── AGPLv3 Runtime ───────────────────────────────────── */}
        <section id="agplv3">
          <SectionHeader
            label="Runtime License"
            title="AGPLv3 — Core Runtime"
            sub="The execution engine, canvas, and application shell are licensed under the GNU Affero General Public License v3."
          />
          <Card>
            <div className="grid sm:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-semibold text-emerald-400 mb-3">You can</h3>
                <ul className="space-y-2">
                  {[
                    'Use for any purpose, including commercial',
                    'Study and modify the source code',
                    'Distribute copies of the software',
                    'Distribute modified versions',
                    'Run privately without disclosure',
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-text-secondary">
                      <svg className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-red-400 mb-3">You must</h3>
                <ul className="space-y-2">
                  {[
                    'Disclose source of distributed copies',
                    'Preserve copyright and license notices',
                    'License modifications under AGPLv3',
                    'Publish source if running as a network service for others',
                    'State changes made to the original',
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-text-secondary">
                      <svg className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-5 pt-5 border-t border-border">
              <a
                href="https://www.gnu.org/licenses/agpl-3.0.en.html"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                Read the full AGPLv3 text →
              </a>
            </div>
          </Card>
        </section>

        {/* ── MIT SDK/API ──────────────────────────────────────── */}
        <section id="mit">
          <SectionHeader
            label="SDK License"
            title="MIT — SDK & Public API"
            sub="The BaseNode class, public node interface, and utility helpers are MIT-licensed to allow closed-source node development."
          />
          <Card>
            <p className="text-text-secondary text-sm leading-relaxed mb-5">
              The MIT License applies to the public SDK surface — specifically{' '}
              <code className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded font-mono">src/nodes/base.py</code>,
              {' '}<code className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded font-mono">src/utils/</code>,
              and the node definition interface. You may build proprietary nodes and pipelines against
              this API and distribute them commercially without disclosing your source code.
            </p>
            <div className="grid sm:grid-cols-3 gap-3">
              {['Use commercially', 'Modify freely', 'Distribute without disclosure', 'Sublicense', 'Private use', 'No warranty'].map((cap) => (
                <div
                  key={cap}
                  className="flex items-center gap-2 p-3 rounded-xl bg-sky-500/5 border border-sky-500/15 text-xs text-sky-300 font-medium"
                >
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {cap}
                </div>
              ))}
            </div>
            <div className="mt-5 pt-5 border-t border-border">
              <a
                href="https://opensource.org/licenses/MIT"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                Read the full MIT License text →
              </a>
            </div>
          </Card>
        </section>

        {/* ── Commercial Licensing ─────────────────────────────── */}
        <section id="commercial">
          <SectionHeader
            label="Commercial"
            title="Commercial Licensing"
            sub="Free for individuals, education, and open productions. Commercial studio deployment requires a license."
          />
          <div className="grid sm:grid-cols-2 gap-4 mb-6">
            {[
              {
                title: 'Studio Pipeline',
                desc: 'Single studio entity — unlimited seats, render farm nodes, artist workstations, and internal pipeline tools.',
                icon: '🎬',
              },
              {
                title: 'SaaS / Cloud',
                desc: 'Hosting the runtime as a networked service accessible to third parties, including cloud render orchestration.',
                icon: '☁️',
              },
              {
                title: 'Proprietary Nodes',
                desc: 'Building and distributing closed-source node packs or plugin libraries that extend Vibrante-Node.',
                icon: '🧩',
              },
              {
                title: 'Enterprise / OEM',
                desc: 'Embedding Vibrante-Node inside a commercial product, multi-studio deployments, or custom integration agreements.',
                icon: '🏢',
              },
            ].map((card) => (
              <Card key={card.title}>
                <div className="text-2xl mb-2">{card.icon}</div>
                <h3 className="text-sm font-semibold text-text-primary mb-1">{card.title}</h3>
                <p className="text-xs text-text-secondary leading-relaxed">{card.desc}</p>
              </Card>
            ))}
          </div>
          <div className="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/20">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-semibold text-amber-400 mb-1">Pricing</p>
                <p className="text-sm text-text-secondary">
                  Commercial licenses are negotiated per engagement based on studio size, deployment scope, and geography.
                  Contact{' '}
                  <a href="mailto:m.kamalvfx@gmail.com" className="text-primary hover:underline">
                    m.kamalvfx@gmail.com
                  </a>{' '}
                  to request a quote. Include studio name, seat count, and intended deployment scope.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ── Enterprise Usage ─────────────────────────────────── */}
        <section id="enterprise">
          <SectionHeader
            label="Enterprise"
            title="Enterprise & Render Farm Usage"
          />
          <Card>
            <div className="space-y-4 text-sm text-text-secondary leading-relaxed">
              <p>
                Enterprise deployments — including multi-studio networks, cloud render farm orchestration,
                and OEM product embedding — are covered by individually negotiated enterprise agreements.
              </p>
              <p>
                Enterprise license holders receive priority support, access to pre-release builds,
                and the option to negotiate custom integration assistance.
              </p>
              <p>
                Render farm nodes running Vibrante-Node automation scripts as part of a commercial
                rendering operation require at minimum a Studio Pipeline license.
              </p>
              <div className="pt-3 border-t border-border">
                <a
                  href="https://github.com/KamalTD/Vibrante-Node/blob/main/COMMERCIAL_LICENSE.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  Read COMMERCIAL_LICENSE.md for full terms →
                </a>
              </div>
            </div>
          </Card>
        </section>

        {/* ── Official Plugins ─────────────────────────────────── */}
        <section id="plugins">
          <SectionHeader
            label="Plugins"
            title="Official Plugins & Node Packs"
            sub="Officially maintained DCC integrations and curated node packs are distributed under commercial terms."
          />
          <Card>
            <p className="text-sm text-text-secondary leading-relaxed mb-5">
              The Houdini Bridge, Maya Headless Executor, Blender Headless Executor, Prism Pipeline
              integration, and Deadline connector are officially maintained components. While the
              open-source runtime they run on is AGPLv3, the curated plugin packages and enterprise
              node libraries require a commercial license for studio deployment.
            </p>
            <p className="text-sm text-text-secondary leading-relaxed">
              Third-party developers may build and distribute their own plugins against the MIT SDK
              without restriction. Naming must follow the{' '}
              <a href="#trademark" className="text-primary hover:underline">Trademark Policy</a>.
            </p>
          </Card>
        </section>

        {/* ── Trademark Policy ─────────────────────────────────── */}
        <section id="trademark">
          <SectionHeader
            label="Trademark"
            title="Trademark Policy"
            sub="Guidelines for using the Vibrante-Node name and logo."
          />
          <div className="grid sm:grid-cols-2 gap-4">
            <Card>
              <h3 className="text-sm font-semibold text-emerald-400 mb-3">Permitted ✓</h3>
              <ul className="space-y-2">
                {[
                  '"[Plugin] for Vibrante-Node"',
                  'Factual articles and tutorials',
                  '"Compatible with Vibrante-Node"',
                  '"Tested on Vibrante-Node v2.0.0"',
                  'Conference talks and academic papers',
                ].map((item) => (
                  <li key={item} className="text-sm text-text-secondary flex items-start gap-2">
                    <svg className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </Card>
            <Card>
              <h3 className="text-sm font-semibold text-red-400 mb-3">Prohibited ✗</h3>
              <ul className="space-y-2">
                {[
                  '"Vibrante-Node [Anything]" — implies official origin',
                  'Logo modification or recolouring',
                  'Domain names containing vibrante-node',
                  'Implying official endorsement',
                  'Merchandise without permission',
                ].map((item) => (
                  <li key={item} className="text-sm text-text-secondary flex items-start gap-2">
                    <svg className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </Card>
          </div>
          <div className="mt-4">
            <a
              href="https://github.com/KamalTD/Vibrante-Node/blob/main/TRADEMARK_POLICY.md"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              Read TRADEMARK_POLICY.md →
            </a>
          </div>
        </section>

        {/* ── CLA ──────────────────────────────────────────────── */}
        <section id="cla">
          <SectionHeader
            label="Contributing"
            title="Contributor License Agreement"
            sub="By submitting a pull request you automatically accept the CLA."
          />
          <Card>
            <div className="grid sm:grid-cols-3 gap-5 text-sm">
              {[
                {
                  title: 'You Retain Copyright',
                  desc: 'Your contribution remains your intellectual property. The CLA grants the project a license to use it, not ownership.',
                },
                {
                  title: 'Dual-License Grant',
                  desc: 'Your contribution may be included in both the open-source AGPLv3/MIT releases and commercial releases of Vibrante-Node.',
                },
                {
                  title: 'No Compensation',
                  desc: 'Contributions are voluntary. The CLA does not entitle contributors to financial compensation from commercial sales.',
                },
              ].map((col) => (
                <div key={col.title}>
                  <h3 className="font-semibold text-text-primary mb-2">{col.title}</h3>
                  <p className="text-text-secondary leading-relaxed">{col.desc}</p>
                </div>
              ))}
            </div>
            <div className="mt-5 pt-5 border-t border-border">
              <a
                href="https://github.com/KamalTD/Vibrante-Node/blob/main/CLA.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                Read CLA.md →
              </a>
            </div>
          </Card>
        </section>

        {/* ── Repository Structure ─────────────────────────────── */}
        <section id="repo">
          <SectionHeader
            label="Repository"
            title="License File Locations"
          />
          <Card className="font-mono text-sm">
            <div className="space-y-1.5 text-text-secondary">
              {[
                { path: '/LICENSE', label: 'AGPLv3 runtime · MIT SDK · CC BY 4.0 docs', color: 'text-emerald-400' },
                { path: '/COMMERCIAL_LICENSE.md', label: 'Studio, SaaS, and enterprise terms', color: 'text-amber-400' },
                { path: '/TRADEMARK_POLICY.md', label: 'Name and logo usage guidelines', color: 'text-violet-400' },
                { path: '/CLA.md', label: 'Contributor License Agreement', color: 'text-sky-400' },
              ].map((row) => (
                <div key={row.path} className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/3 transition-colors">
                  <span className={`${row.color} flex-shrink-0 w-56`}>{row.path}</span>
                  <span className="text-text-secondary text-xs">{row.label}</span>
                </div>
              ))}
            </div>
          </Card>
        </section>

        {/* ── FAQ ──────────────────────────────────────────────── */}
        <section id="faq">
          <SectionHeader label="FAQ" title="Frequently Asked Questions" />
          <div className="space-y-3">
            {faq.map((item) => (
              <Card key={item.q}>
                <h3 className="text-sm font-semibold text-text-primary mb-2">{item.q}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{item.a}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* ── Contact CTA ──────────────────────────────────────── */}
        <section id="contact">
          <div className="rounded-3xl bg-primary/5 border border-primary/20 p-10 text-center">
            <h2 className="text-2xl font-bold text-text-primary mb-3">
              Questions about licensing?
            </h2>
            <p className="text-text-secondary mb-8 max-w-xl mx-auto">
              For commercial licensing inquiries, trademark permissions, or enterprise agreements,
              contact the author directly. Include your studio name, deployment scope, and start date.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <a
                href="mailto:m.kamalvfx@gmail.com"
                className="inline-flex items-center gap-2 px-7 py-3.5 text-base font-semibold text-white bg-primary hover:bg-primary/90 rounded-xl transition-all hover:shadow-glow-purple hover:-translate-y-0.5"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                m.kamalvfx@gmail.com
              </a>
              <Link
                href="/docs"
                className="inline-flex items-center gap-2 px-7 py-3.5 text-base font-semibold text-primary border border-primary/40 hover:border-primary hover:bg-primary/5 rounded-xl transition-all"
              >
                Read the Docs
              </Link>
            </div>
          </div>
        </section>

      </div>

      <Footer />
    </main>
  )
}
