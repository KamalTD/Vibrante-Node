import Link from 'next/link'

const footerLinks = {
  Product: [
    { label: 'Features', href: '/#features' },
    { label: 'Showcase', href: '/showcase' },
    { label: 'Screenshots', href: '/#screenshots' },
    { label: 'Integrations', href: '/#integrations' },
    { label: 'Studio', href: '/studio' },
  ],
  Developers: [
    { label: 'Getting Started', href: '/docs' },
    { label: 'Node Development', href: '/developers' },
    { label: 'API Reference', href: '/docs#api' },
    { label: 'Custom Nodes', href: '/developers#custom-nodes' },
    { label: 'Examples', href: '/docs#examples' },
  ],
  Integrations: [
    { label: 'Houdini Bridge', href: '/developers#houdini' },
    { label: 'Maya Headless', href: '/developers#maya' },
    { label: 'Blender Headless', href: '/developers#blender' },
    { label: 'Prism Pipeline', href: '/developers#prism' },
    { label: 'Deadline', href: '/developers#deadline' },
  ],
  Community: [
    { label: 'GitHub', href: 'https://github.com/vibrante-node' },
    { label: 'Documentation', href: '/docs' },
    { label: 'Release Notes', href: '/docs#releases' },
    { label: 'Contribution Guide', href: '/docs#contributing' },
  ],
}

export function Footer() {
  return (
    <footer className="bg-surface border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main footer */}
        <div className="py-16 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-10">
          {/* Brand */}
          <div className="col-span-2 md:col-span-3 lg:col-span-1">
            <Link href="/" className="inline-flex items-center gap-3 mb-4 group">
              <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center border border-primary/30">
                <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="6" cy="6" r="3" strokeWidth={2} />
                  <circle cx="18" cy="6" r="3" strokeWidth={2} />
                  <circle cx="18" cy="18" r="3" strokeWidth={2} />
                  <circle cx="6" cy="18" r="3" strokeWidth={2} />
                  <path strokeLinecap="round" strokeWidth={2} d="M9 6h6M18 9v6M15 18H9M6 15V9" />
                </svg>
              </div>
              <span className="font-bold text-lg text-text-primary">
                Vibrante<span className="text-primary">-Node</span>
              </span>
            </Link>
            <p className="text-sm text-text-secondary leading-relaxed mb-6 max-w-xs">
              Open-source node-based automation platform for VFX studios, AI engineers, and pipeline developers.
            </p>
            {/* Social links */}
            <div className="flex gap-3">
              <a
                href="https://github.com/vibrante-node"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 text-text-secondary hover:text-text-primary border border-border hover:border-primary/30 transition-all"
                aria-label="GitHub"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a
                href="mailto:contact@vibrante-node.io"
                className="w-9 h-9 flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 text-text-secondary hover:text-text-primary border border-border hover:border-primary/30 transition-all"
                aria-label="Email"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-text-secondary mb-4">
                {category}
              </h3>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-text-secondary hover:text-text-primary transition-colors"
                      {...(link.href.startsWith('http') ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="py-6 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-text-secondary">
            © {new Date().getFullYear()} Vibrante-Node. Open source under MIT License.
          </p>
          <div className="flex items-center gap-6">
            <span className="text-xs text-text-secondary/60 font-mono">
              v2.0.0 — Python 3.10+ · PyQt5 · asyncio
            </span>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-text-secondary">Production Ready</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
