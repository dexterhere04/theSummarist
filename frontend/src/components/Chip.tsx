import type { JSX, ReactNode } from 'react'

interface ChipProps {
  children: ReactNode
  tone?: 'neutral' | 'accent' | 'ok' | 'error'
  icon?: string
}

const tones: Record<NonNullable<ChipProps['tone']>, string> = {
  neutral: 'bg-surface-lowest border border-line text-ink-variant',
  accent: 'bg-accent-tint border border-accent/25 text-accent-strong',
  ok: 'bg-ok-soft border border-ok/25 text-ok',
  error: 'bg-error-soft border border-error/25 text-error',
}

export function Chip({ children, tone = 'neutral', icon }: ChipProps): JSX.Element {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-[3px] border px-2 py-0.5 text-[11.5px] font-medium tracking-[0.02em] ${tones[tone]}`}
    >
      {icon && (
        <span
          aria-hidden="true"
          className="material-symbols-rounded text-[13px] leading-none"
        >
          {icon}
        </span>
      )}
      {children}
    </span>
  )
}
