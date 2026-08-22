import type { JSX } from 'react'

interface IconProps {
  name: string
  className?: string
  filled?: boolean
}

export function Icon({ name, className = '', filled = false }: IconProps): JSX.Element {
  return (
    <span
      aria-hidden="true"
      className={`material-symbols-rounded ${filled ? 'is-filled' : ''} ${className}`}
    >
      {name}
    </span>
  )
}
