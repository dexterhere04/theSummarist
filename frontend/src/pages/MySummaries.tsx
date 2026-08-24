import { useEffect, useState } from 'react'
import type { CSSProperties, JSX } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import type { SummaryItem as SummaryData } from '../lib/types'
import { Chip } from '../components/Chip'
import { Icon } from '../components/Icon'

const delay = (i: number): CSSProperties => ({ ['--reveal-delay' as string]: `${i * 70}ms` })

const TABS: { label: string; value: 'all' | 'recent' | 'favorites' }[] = [
  { label: 'All', value: 'all' },
  { label: 'Recent', value: 'recent' },
  { label: 'Favorites', value: 'favorites' },
]

export function MySummaries({
  initialTab = 'all',
}: {
  initialTab?: 'all' | 'recent' | 'favorites'
}): JSX.Element {
  const [searchParams] = useSearchParams()
  const q = searchParams.get('q') ?? ''

  const [tab, setTab] = useState<'all' | 'recent' | 'favorites'>(initialTab)
  const [items, setItems] = useState<SummaryData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => setTab(initialTab), [initialTab])

  useEffect(() => {
    setLoading(true)
    api
      .listSummaries({ tab, q: q || undefined })
      .then((page) => setItems(page.items))
      .catch(() => setItems([]))
      .finally(() => setLoading(false))
  }, [tab, q])

  return (
    <div className="mx-auto max-w-6xl px-4 md:px-8 py-10 md:py-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-1">
        <div>
          <p className="eyebrow text-accent">The Library</p>
          <h1 className="font-display text-3xl md:text-[40px] font-semibold tracking-tight text-ink mt-2">
            My Summaries
          </h1>
          {q && (
            <p className="mt-2 text-[14px] text-ink-variant">
              Results for “{q}”
            </p>
          )}
        </div>
        <div className="flex items-center gap-0 border border-line-strong w-fit">
          {TABS.map((t, i) => (
            <button
              key={t.value}
              type="button"
              onClick={() => setTab(t.value)}
              className={`px-4 py-2 text-[13px] font-medium transition-colors ${
                tab === t.value
                  ? 'bg-accent text-surface-lowest'
                  : 'text-ink-variant hover:bg-surface-low'
              } ${i > 0 ? 'border-l border-line-strong' : ''}`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>
      <div className="rule-thick-thin mt-5 mb-8" />

      {loading ? (
        <div className="py-24 text-center">
          <Icon name="sync" className="text-[32px] text-accent animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="py-16 flex flex-col items-center text-center">
          <div className="w-14 h-14 rounded-[4px] bg-surface-low text-accent grid place-items-center mb-6 border border-line">
            <Icon name="folder_open" className="text-[26px]" />
          </div>
          <h2 className="font-display text-xl font-semibold text-ink">Empty shelf</h2>
          <p className="mt-3 text-[15px] text-ink-variant max-w-sm leading-relaxed">
            Nothing here yet. Start by uploading a document to generate your first summary.
          </p>
          <Link to="/" className="mt-7">
            <Chip tone="accent">Upload a document →</Chip>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {items.map((s, i) => (
            <Link
              key={s.id}
              to={`/summary/${s.id}`}
              className="group relative border border-line bg-surface-lowest hover:border-accent hover:shadow-raised transition-all flex flex-col reveal"
              style={delay(i)}
            >
              <div className="h-[3px] bg-accent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="p-5 flex flex-col flex-1">
                <div className="flex items-start gap-3 mb-4">
                  <div className="w-10 h-10 rounded-[4px] bg-surface-low text-accent grid place-items-center shrink-0">
                    <Icon name="description" className="text-[20px]" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-display font-semibold text-[16px] leading-snug text-ink line-clamp-1 group-hover:text-accent transition-colors">
                      {s.title}
                    </h3>
                    <p className="font-mono text-[11px] text-ink-muted mt-1">
                      {s.format} · {s.pages ?? '—'} pp. · {s.date}
                    </p>
                  </div>
                </div>

                <p className="text-[14px] text-ink-variant leading-relaxed line-clamp-3 flex-1">
                  {s.excerpt || s.tldr}
                </p>

                <div className="flex gap-1.5 mt-5 pt-4 border-t border-line">
                  <Chip tone="accent">{s.category}</Chip>
                  <Chip>{s.kind}</Chip>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
