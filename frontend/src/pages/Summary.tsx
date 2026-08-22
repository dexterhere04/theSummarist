import type { JSX } from 'react'
import { useParams, Navigate } from 'react-router-dom'
import { Button } from '../components/Button'
import { Chip } from '../components/Chip'
import { Icon } from '../components/Icon'
import { summaries } from '../lib/data'

export function Summary(): JSX.Element {
  const { id } = useParams()
  const summary = summaries.find((s) => s.id === id)

  if (!summary) return <Navigate to="/summaries" replace />

  return (
    <div className="mx-auto max-w-[1240px] px-4 md:px-8 py-6 md:py-8">
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1 min-w-0 flex flex-col gap-5">
          <div className="border-b border-line pb-6">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="min-w-0">
                <h2 className="font-mono text-[11px] uppercase tracking-[0.2em] text-accent mb-2">
                  Generated Summary
                </h2>
                <h1 className="font-display text-3xl md:text-[38px] font-semibold tracking-tight text-ink leading-[1.08]">
                  {summary.title}
                </h1>
              </div>
              <div className="flex items-center gap-0.5 shrink-0">
                {[
                  { icon: 'refresh', label: 'Regenerate' },
                  { icon: 'download', label: 'Download' },
                  { icon: 'bookmark_border', label: 'Favorite' },
                  { icon: 'share', label: 'Share' },
                ].map((a) => (
                  <button
                    key={a.label}
                    type="button"
                    title={a.label}
                    className="w-9 h-9 rounded-[3px] grid place-items-center text-ink-variant hover:bg-surface-container hover:text-accent transition-colors"
                  >
                    <Icon name={a.icon} className="text-[19px]" />
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 mt-5">
              <Chip>{summary.length} Length</Chip>
              <span className="text-line">·</span>
              <Chip tone="accent">{summary.kind}</Chip>
              <span className="text-line">·</span>
              <span className="inline-flex items-center gap-1.5 text-[13px] text-ink-variant">
                <Icon name="schedule" className="text-[14px]" />
                Generated just now
              </span>
            </div>
          </div>

          <article className="border border-line bg-surface-lowest overflow-hidden">
            <div className="px-6 md:px-8 py-7 bg-surface-low border-b border-line">
              <div className="flex items-center gap-3">
                <span className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-accent border border-accent/30 bg-accent-soft px-2 py-0.5 rounded-[3px]">
                  TL;DR
                </span>
                <h2 className="font-display font-semibold text-[18px] text-ink">
                  Quick Summary
                </h2>
              </div>
              <p className="mt-4 text-[17px] md:text-[17.5px] leading-[1.7] text-ink dropcap max-w-[70ch]">
                {summary.tldr}
              </p>
            </div>

            <div className="px-6 md:px-8 py-7">
              <h2 className="font-display font-semibold text-[20px] text-ink">
                Key Takeaways
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mt-5">
                {summary.takeaways.map((t, i) => (
                  <div
                    key={t.title}
                    className="border border-line p-4 bg-surface-lowest hover:border-line-strong transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-[3px] bg-accent text-surface-lowest grid place-items-center font-mono text-[12px] font-semibold">
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <h3 className="text-[16px] font-semibold text-ink">
                        {t.title}
                      </h3>
                    </div>
                    <p className="mt-3 text-[15.5px] leading-[1.65] text-ink-variant">
                      {t.body}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="px-6 md:px-8 py-7 border-t border-line">
              <h2 className="font-display font-semibold text-[20px] text-ink">
                Detailed Analysis
              </h2>
              <div className="mt-6 space-y-8">
                {summary.sections.map((s, i) => (
                  <div key={s.heading} className="max-w-[70ch]">
                    <h3 className="font-mono text-[13px] uppercase tracking-[0.14em] text-ink-variant">
                      {String(i + 1).padStart(2, '0')}. {s.heading}
                    </h3>
                    <p className="mt-2.5 text-[17px] leading-[1.75] text-ink">
                      {s.body}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </article>
        </div>

        <aside className="lg:w-[320px] shrink-0 flex flex-col gap-5">
          <div className="border border-line bg-surface-lowest p-5">
            <h3 className="eyebrow text-ink-muted mb-4">Listen</h3>
            <div className="flex items-center gap-3.5">
              <button
                type="button"
                className="w-11 h-11 rounded-[3px] bg-accent text-surface-lowest grid place-items-center hover:bg-accent-strong transition-colors shrink-0"
              >
                <Icon name="play_arrow" className="text-[24px]" />
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-end gap-[3px] h-8">
                  {[4, 8, 3, 7, 5, 2, 6, 4, 2, 5, 3, 7, 4, 6, 2, 5].map(
                    (h, i) => (
                      <div
                        key={i}
                        className="w-[3px] rounded-full bg-accent/50"
                        style={{ height: `${h * 4}px` }}
                      />
                    ),
                  )}
                </div>
                <div className="flex justify-between font-mono text-[11px] text-ink-muted mt-2">
                  <span>0:00</span>
                  <span>2:15</span>
                </div>
              </div>
            </div>
          </div>

          <div className="border border-line bg-surface-lowest p-5">
            <h3 className="eyebrow text-ink-muted mb-4">Source Document</h3>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-[4px] bg-surface-low text-accent grid place-items-center shrink-0">
                <Icon name="description" className="text-[20px]" />
              </div>
              <div className="min-w-0 leading-tight">
                <div className="text-[13.5px] font-medium text-ink truncate">
                  {summary.source}
                </div>
                <div className="text-[12px] text-ink-muted mt-0.5">
                  {summary.pages} pp. · {summary.words.toLocaleString()} words
                </div>
              </div>
            </div>
            <Button variant="secondary" size="sm" className="w-full mt-4">
              View extracted text
            </Button>
          </div>

          <div className="border border-line bg-surface-lowest p-5">
            <h3 className="eyebrow text-ink-muted mb-3">Notable Quote</h3>
            <blockquote className="ai-highlight px-4 py-3">
              <p className="text-[14.5px] leading-relaxed text-ink italic">
                &ldquo;{summary.highlight}&rdquo;
              </p>
            </blockquote>
          </div>
        </aside>
      </div>
    </div>
  )
}
