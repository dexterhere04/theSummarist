import type { CSSProperties, JSX } from 'react'
import { Link } from 'react-router-dom'
import { Chip } from '../components/Chip'
import { Icon } from '../components/Icon'
import { summaries } from '../lib/data'

const delay = (i: number): CSSProperties => ({ ['--reveal-delay' as string]: `${i * 70}ms` })

export function MySummaries(): JSX.Element {
  return (
    <div className="mx-auto max-w-6xl px-4 md:px-8 py-10 md:py-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-1">
        <div>
          <p className="eyebrow text-accent">The Library</p>
          <h1 className="font-display text-3xl md:text-[40px] font-semibold tracking-tight text-ink mt-2">
            My Summaries
          </h1>
        </div>
        <div className="flex items-center gap-0 border border-line-strong w-fit">
          {['All', 'Recent', 'Favorites'].map((tab, i) => (
            <button
              key={tab}
              type="button"
              className={`px-4 py-2 text-[13px] font-medium transition-colors ${
                i === 0
                  ? 'bg-accent text-surface-lowest'
                  : 'text-ink-variant hover:bg-surface-low'
              } ${i > 0 ? 'border-l border-line-strong' : ''}`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>
      <div className="rule-thick-thin mt-5 mb-8" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {summaries.map((s, i) => (
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
                    {s.format} · {s.pages} pp. · {s.date}
                  </p>
                </div>
              </div>

              <p className="text-[14px] text-ink-variant leading-relaxed line-clamp-3 flex-1">
                {s.excerpt}
              </p>

              <div className="flex gap-1.5 mt-5 pt-4 border-t border-line">
                <Chip tone="accent">{s.category}</Chip>
                <Chip>{s.kind}</Chip>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
