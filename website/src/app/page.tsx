import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { Hero } from '@/components/home/Hero'
import { Features } from '@/components/home/Features'
import { Screenshots } from '@/components/home/Screenshots'
import { Integrations } from '@/components/home/Integrations'
import { WorkflowShowcase } from '@/components/home/WorkflowShowcase'
import { DeveloperSection } from '@/components/home/DeveloperSection'
import { CTASection } from '@/components/home/CTASection'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <Features />
      <Screenshots />
      <Integrations />
      <WorkflowShowcase />
      <DeveloperSection />
      <CTASection />
      <Footer />
    </main>
  )
}
