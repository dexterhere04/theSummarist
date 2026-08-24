import { useEffect, useState } from 'react'
import type { JSX } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import type { Document as Doc } from '../lib/types'
import { FormatBadge } from '../components/FormatBadge'
import { Icon } from '../components/Icon'

function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  if (bytes >= 1024) return `${Math.round(bytes / 1024)} KB`
  return `${bytes} B`
}

export function RecentDocuments(): JSX.Element {
  const [docs, setDocs] = useState<Doc[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .listDocuments({ per_page: 50 })
      .then((page) => setDocs(page.items))
      .catch(() => setDocs([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="mx-auto max-w-5xl px-4 md:px-8 py-10 md:py-12">
      <p className="eyebrow text-accent">Library</p>
      <h1 className="font-display text-3xl md:text-[40px] font-semibold tracking-tight text-ink mt-2">
        Recent Documents
      </h1>
      <div className="rule-thick-thin mt-5 mb-8" />

      {loading ? (
        <div className="py-24 text-center">
          <Icon name="sync" className="text-[32px] text-accent animate-spin" />
        </div>
      ) : docs.length === 0 ? (
        <div className="py-16 flex flex-col items-center text-center">
          <div className="w-14 h-14 rounded-[4px] bg-surface-low text-accent grid place-items-center mb-6 border border-line">
            <Icon name="history" className="text-[26px]" />
          </div>
          <h2 className="font-display text-xl font-semibold text-ink">No documents yet</h2>
          <p className="mt-3 text-[15px] text-ink-variant max-w-sm leading-relaxed">
            Upload a file from the dashboard and it will appear here.
          </p>
          <Link
            to="/"
            className="mt-7 inline-flex items-center gap-2 h-10 px-5 rounded bg-accent text-surface-lowest text-sm font-medium hover:bg-accent-strong transition-colors"
          >
            <Icon name="add" className="text-[18px]" />
            New Summary
          </Link>
        </div>
      ) : (
        <div className="flex flex-col">
          {docs.map((d, i) => (
            <Link
              key={d.id}
              to={`/document/${d.id}`}
              className={`group flex items-center gap-4 px-3 py-4 hover:bg-surface-lowest transition-colors ${
                i < docs.length - 1 ? 'border-b border-line' : ''
              }`}
            >
              <FormatBadge format={d.format} />
              <div className="flex-1 min-w-0">
                <h3 className="text-[15px] font-medium text-ink truncate group-hover:text-accent transition-colors">
                  {d.file_name}
                </h3>
                <p className="font-mono text-[11px] text-ink-muted mt-0.5">
                  {(d.words ?? 0).toLocaleString()} words ·{' '}
                  {new Date(d.created_at).toLocaleString()}
                </p>
              </div>
              <span className="hidden sm:block text-[12.5px] text-ink-muted">
                {formatSize(d.size_bytes)}
              </span>
              <span
                className={`font-mono text-[9.5px] uppercase tracking-[0.14em] px-1.5 py-[3px] rounded-[3px] border ${
                  d.status === 'ready'
                    ? 'text-ok border-ok/40 bg-ok-soft/50'
                    : d.status === 'failed'
                      ? 'text-error border-error/40 bg-error-soft/50'
                      : 'text-ink-variant border-line-strong/50 bg-surface-container'
                }`}
              >
                {d.status}
              </span>
              <Icon
                name="chevron_right"
                className="text-[18px] text-ink-muted group-hover:text-accent transition-colors"
              />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
