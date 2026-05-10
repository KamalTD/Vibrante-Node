import fs from 'fs'
import path from 'path'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { MarkdownRenderer } from '@/components/docs/MarkdownRenderer'
import { docSections } from '@/components/docs/docSections'

interface Props {
  params: { slug: string }
}

export function generateStaticParams() {
  return docSections.map((s) => ({ slug: s.id }))
}

export function generateMetadata({ params }: Props) {
  const section = docSections.find((s) => s.id === params.slug)
  if (!section) return {}
  return {
    title: `${section.title} — Vibrante-Node Docs`,
    description: section.summary,
  }
}

function readMarkdown(file: string): string | null {
  try {
    const mdPath = path.join(process.cwd(), 'src', 'app', 'docs', 'docs_src', `${file}.md`)
    return fs.readFileSync(mdPath, 'utf-8')
  } catch {
    return null
  }
}

export default function DocPage({ params }: Props) {
  const section = docSections.find((s) => s.id === params.slug)
  if (!section) notFound()

  const content = readMarkdown(section.file)
  if (!content) notFound()

  const currentIdx = docSections.indexOf(section)
  const prevSection = currentIdx > 0 ? docSections[currentIdx - 1] : null
  const nextSection = currentIdx < docSections.length - 1 ? docSections[currentIdx + 1] : null

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="pt-16 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-4 gap-0 min-h-screen">
            {/* Sidebar */}
            <aside className="lg:col-span-1 border-r border-border pt-8 pb-8 pr-0 lg:pr-6">
              <div className="mb-6">
                <Link href="/docs" className="text-xl font-bold text-text-primary hover:text-primary transition-colors">
                  Documentation
                </Link>
                <p className="text-sm text-text-secondary mt-1">v2.0.0</p>
              </div>

              <nav className="flex flex-col gap-0.5">
                {docSections.map((s) => {
                  const isActive = s.id === params.slug
                  return (
                    <Link
                      key={s.id}
                      href={`/docs/${s.id}`}
                      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm transition-all duration-150 ${
                        isActive
                          ? 'bg-primary/10 text-primary font-medium'
                          : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
                      }`}
                    >
                      <span className="text-base">{s.icon}</span>
                      <span className="truncate">{s.title}</span>
                      {isActive && (
                        <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                      )}
                    </Link>
                  )
                })}
              </nav>
            </aside>

            {/* Main content */}
            <article className="lg:col-span-3 pt-8 pb-16 lg:pl-10 min-w-0">
              {/* Breadcrumb */}
              <div className="flex items-center gap-2 text-xs text-text-secondary mb-6">
                <Link href="/docs" className="hover:text-primary transition-colors">
                  Docs
                </Link>
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <span className="text-text-primary">{section.title}</span>
              </div>

              {/* Markdown content */}
              <MarkdownRenderer content={content} />

              {/* Prev / Next navigation */}
              <div className="mt-12 pt-8 border-t border-border grid grid-cols-2 gap-4">
                {prevSection ? (
                  <Link
                    href={`/docs/${prevSection.id}`}
                    className="flex flex-col gap-1 p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-white/2 transition-all group"
                  >
                    <span className="text-xs text-text-secondary">← Previous</span>
                    <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors">
                      {prevSection.icon} {prevSection.title}
                    </span>
                  </Link>
                ) : (
                  <div />
                )}

                {nextSection ? (
                  <Link
                    href={`/docs/${nextSection.id}`}
                    className="flex flex-col gap-1 p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-white/2 transition-all group text-right"
                  >
                    <span className="text-xs text-text-secondary">Next →</span>
                    <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors">
                      {nextSection.icon} {nextSection.title}
                    </span>
                  </Link>
                ) : (
                  <div />
                )}
              </div>
            </article>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
