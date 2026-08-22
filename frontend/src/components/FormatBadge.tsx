import type { JSX } from 'react'
import type { DocFormat } from '../lib/types'

const colors: Record<DocFormat, string> = {
  PDF: 'text-error border-error/40 bg-error-soft/50',
  DOC: 'text-accent border-accent/40 bg-accent-soft/50',
  DOCX: 'text-accent border-accent/40 bg-accent-soft/50',
  PPTX: 'text-ink-variant border-line-strong/50 bg-surface-container',
  TXT: 'text-ink-variant border-line-strong/50 bg-surface-container',
  WEB: 'text-ok border-ok/40 bg-ok-soft/50',
}

export function FormatBadge({ format }: { format: DocFormat }): JSX.Element {
  return (
    <span
      className={`font-mono text-[9.5px] font-semibold tracking-[0.14em] px-1.5 py-[3px] rounded-[3px] border ${colors[format]}`}
    >
      {format}
    </span>
  )
}
