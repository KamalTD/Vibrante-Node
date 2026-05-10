'use client'

import { motion } from 'framer-motion'
import { clsx } from 'clsx'

interface SectionHeaderProps {
  badge?: string
  title: string
  titleGradient?: string
  subtitle?: string
  align?: 'left' | 'center' | 'right'
  className?: string
}

export function SectionHeader({
  badge,
  title,
  titleGradient,
  subtitle,
  align = 'center',
  className,
}: SectionHeaderProps) {
  const alignClass = {
    left: 'text-left items-start',
    center: 'text-center items-center',
    right: 'text-right items-end',
  }[align]

  return (
    <motion.div
      className={clsx('flex flex-col gap-4', alignClass, className)}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      {badge && (
        <span className="inline-flex items-center gap-2 px-3 py-1 text-xs font-semibold text-primary bg-primary/10 border border-primary/20 rounded-full w-fit">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          {badge}
        </span>
      )}
      <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-text-primary">
        {title}
        {titleGradient && (
          <span className="gradient-text"> {titleGradient}</span>
        )}
      </h2>
      {subtitle && (
        <p className="text-lg text-text-secondary max-w-2xl leading-relaxed">
          {subtitle}
        </p>
      )}
    </motion.div>
  )
}
