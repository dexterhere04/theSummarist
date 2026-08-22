import { useState } from 'react'
import type { JSX } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'
import { extractedDoc } from '../lib/data'

type Format = 'bullets' | 'paragraph'
type Detail = 'Concise' | 'Medium' | 'Detailed'

const detailLabels: Record<Detail, string> = {
  Concise: 'Concise',
  Medium: 'Medium',
  Detailed: 'Detailed',
}

export function ExtractedText(): JSX.Element {
  const navigate = useNavigate()
  const [format, setFormat] = useState<Format>('bullets')
  const [detail, setDetail] = useState<Detail>('Concise')

  return (
    <div className="mx-auto max-w-[1240px] px-4 md:px-8 py-6 md:py-8">
      <div className="flex flex-col lg:flex-row gap-6">
        <section className="flex-1 min-w-0 border border-line bg-surface-lowest overflow-hidden flex flex-col">
          <div className="flex items-center justify-between gap-3 px-4 md:px-5 h-14 border-b border-line bg-surface">
            <div className="flex items-center gap-2.5 min-w-0">
              <Icon name="description" className="text-[18px] text-ink-variant" />
              <span className="text-sm font-medium text-ink truncate">
                {extractedDoc.fileName}
              </span>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <div className="relative hidden sm:block mr-1">
                <Icon
                  name="search"
                  className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[16px] text-ink-muted"
                />
                <input
                  type="text"
                  placeholder="Search text…"
                  className="h-8 pl-8 pr-3 w-44 rounded-[3px] border border-line bg-surface-lowest text-[13px] placeholder:text-ink-muted focus:outline-none focus:border-accent transition-colors"
                />
              </div>
              <button
                type="button"
                title="Copy text"
                className="w-8 h-8 rounded-[3px] grid place-items-center text-ink-variant hover:bg-surface-low hover:text-accent transition-colors"
              >
                <Icon name="content_copy" className="text-[18px]" />
              </button>
              <button
                type="button"
                title="Download TXT"
                className="w-8 h-8 rounded-[3px] grid place-items-center text-ink-variant hover:bg-surface-low hover:text-accent transition-colors"
              >
                <Icon name="download" className="text-[18px]" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-5 md:px-10 py-9">
            <article className="max-w-[700px] mx-auto">
              <p className="eyebrow text-accent">Extracted text</p>
              <h1 className="font-display text-3xl md:text-[34px] font-semibold tracking-tight text-ink leading-tight mt-2">
                {extractedDoc.title}
              </h1>
              <div className="rule-thick-thin mt-5 mb-8" />
              <div className="space-y-9">
                {extractedDoc.body.map((section, si) => (
                  <div key={section.heading}>
                    <h2 className="font-display text-xl font-semibold text-ink mb-5">
                      {section.heading}
                    </h2>
                    <div className="space-y-5">
                      {section.paragraphs.map((p, i) => (
                        <p
                          key={i}
                          className={`text-[16px] leading-[1.7] text-ink-variant ${
                            si === 0 && i === 0 ? 'dropcap' : ''
                          }`}
                        >
                          {p}
                        </p>
                      ))}
                      {section.bullets && (
                        <ul className="space-y-3.5 pl-1">
                          {section.bullets.map((b, i) => (
                            <li key={i} className="flex items-start gap-3">
                              <span className="font-mono text-[12px] text-accent mt-[3px] shrink-0">
                                §
                              </span>
                              <span className="text-[16px] leading-[1.7] text-ink-variant">
                                {b}
                              </span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>

        <aside className="lg:w-[340px] shrink-0 flex flex-col gap-5">
          <div className="border border-line bg-surface-lowest p-5">
            <h3 className="eyebrow text-ink-muted mb-4">Document Properties</h3>
            <dl className="divide-y divide-line">
              {[
                ['Format', extractedDoc.format],
                ['OCR Method', extractedDoc.ocr],
                ['Word Count', extractedDoc.words.toLocaleString()],
                ['Pages', String(extractedDoc.pages)],
                ['Language', extractedDoc.lang],
              ].map(([k, v]) => (
                <div
                  key={k}
                  className="flex items-center justify-between py-2.5 text-[13.5px]"
                >
                  <dt className="text-ink-variant">{k}</dt>
                  <dd className="font-mono text-[12px] font-medium text-ink">{v}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="border border-line bg-surface-lowest p-5">
            <h3 className="font-display font-semibold text-[17px] text-ink">
              Create Summary
            </h3>
            <p className="mt-1.5 text-[13.5px] text-ink-variant leading-relaxed">
              The text has been successfully extracted. Configure your summary
              parameters to generate AI insights.
            </p>

            <div className="mt-6 space-y-6">
              <div>
                <label className="eyebrow text-ink-muted block mb-3">
                  Summary Format
                </label>
                <div className="grid grid-cols-2 gap-2.5">
                  <button
                    type="button"
                    onClick={() => setFormat('bullets')}
                    className={`flex flex-col items-center gap-1.5 rounded-[3px] border py-3 text-[13px] font-medium transition-colors ${
                      format === 'bullets'
                        ? 'border-accent bg-accent-tint text-accent-strong'
                        : 'border-line text-ink-variant hover:border-line-strong'
                    }`}
                  >
                    <Icon name="view_list" className="text-[20px]" filled />
                    Bullet Points
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormat('paragraph')}
                    className={`flex flex-col items-center gap-1.5 rounded-[3px] border py-3 text-[13px] font-medium transition-colors ${
                      format === 'paragraph'
                        ? 'border-accent bg-accent-tint text-accent-strong'
                        : 'border-line text-ink-variant hover:border-line-strong'
                    }`}
                  >
                    <Icon name="notes" className="text-[20px]" />
                    Paragraph
                  </button>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="eyebrow text-ink-muted">Detail Level</label>
                  <span className="font-mono text-[12px] font-medium text-accent">
                    {detailLabels[detail]}
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={2}
                  step={1}
                  value={detail === 'Concise' ? 0 : detail === 'Medium' ? 1 : 2}
                  onChange={(e) => {
                    const vals: Detail[] = ['Concise', 'Medium', 'Detailed']
                    setDetail(vals[Number(e.target.value)])
                  }}
                  className="w-full accent-accent"
                  aria-label="Detail level"
                />
                <div className="flex justify-between font-mono text-[10px] text-ink-muted mt-1.5">
                  <span>Short</span>
                  <span>Medium</span>
                  <span>Detailed</span>
                </div>
              </div>
            </div>

            <Button
              className="w-full mt-7"
              size="lg"
              icon="arrow_forward"
              onClick={() => navigate('/configure')}
            >
              Configure Summary
            </Button>
          </div>
        </aside>
      </div>
    </div>
  )
}
