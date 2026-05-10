import { clsx } from 'clsx'
import React from 'react'

type BadgeVariant = 'default' | 'primary' | 'secondary' | 'houdini' | 'maya' | 'blender' | 'prism' | 'deadline' | 'success' | 'warning'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
  dot?: boolean
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-white/5 text-text-secondary border-white/10',
  primary: 'bg-primary/10 text-primary border-primary/20',
  secondary: 'bg-secondary/10 text-secondary border-secondary/20',
  houdini: 'bg-houdini/10 text-houdini border-houdini/20',
  maya: 'bg-maya/10 text-maya border-maya/20',
  blender: 'bg-blender/10 text-blender border-blender/20',
  prism: 'bg-prism/10 text-prism border-prism/20',
  deadline: 'bg-deadline/10 text-deadline border-deadline/20',
  success: 'bg-green-500/10 text-green-400 border-green-500/20',
  warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
}

export function Badge({ children, variant = 'default', className, dot }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full border',
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span
          className={clsx('w-1.5 h-1.5 rounded-full', {
            'bg-primary': variant === 'primary',
            'bg-secondary': variant === 'secondary',
            'bg-houdini': variant === 'houdini',
            'bg-maya': variant === 'maya',
            'bg-blender': variant === 'blender',
            'bg-prism': variant === 'prism',
            'bg-deadline': variant === 'deadline',
            'bg-green-400': variant === 'success',
            'bg-yellow-400': variant === 'warning',
            'bg-text-secondary': variant === 'default',
          })}
        />
      )}
      {children}
    </span>
  )
}
