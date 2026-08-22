import type { JSX } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'

export function EmptyState({ label }: { label: string }): JSX.Element {
  return (
    <div className="mx-auto max-w-5xl px-4 md:px-8 py-24 flex flex-col items-center text-center">
      <div className="w-14 h-14 rounded-[4px] bg-surface-low text-accent grid place-items-center mb-6 border border-line">
        <Icon name="folder_open" className="text-[26px]" />
      </div>
      <p className="eyebrow text-ink-muted">Empty shelf</p>
      <h1 className="font-display text-3xl font-semibold text-ink mt-2">{label}</h1>
      <p className="mt-3 text-[15px] text-ink-variant max-w-sm leading-relaxed">
        Nothing here yet. Start by uploading a document to generate your first
        summary.
      </p>
      <Link to="/" className="mt-7">
        <Button icon="add">New Summary</Button>
      </Link>
    </div>
  )
}
