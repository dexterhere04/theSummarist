import { useEffect, useState } from 'react'
import type { JSX } from 'react'
import {
  Navigate,
  useLocation,
  useNavigate,
  useSearchParams,
} from 'react-router-dom'
import { api } from '../lib/api'
import type {
  DetailLevel,
  ExtractedText as ExtractedTextData,
  SummaryFormat,
  SummaryLength,
  SummaryStyle,
} from '../lib/types'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'

const styles: { value: SummaryStyle; label: string; icon: string; desc: string }[] = [
  {
    value: 'executive',
    label: 'Executive Summary',
    icon: 'corporate_fare',
    desc: 'High-level overview focusing on main conclusions and decisions.',
  },
  {
    value: 'key_points',
    label: 'Key Points',
    icon: 'format_list_bulleted',
    desc: 'Bullet-point list extracting the most critical facts.',
  },
  {
    value: 'detailed',
    label: 'Detailed Summary',
    icon: 'article',
    desc: 'Comprehensive breakdown preserving structural flow.',
  },
  {
    value: 'study_notes',
    label: 'Study Notes',
    icon: 'school',
    desc: 'Optimized for learning and memorization.',
  },
  {
    value: 'action_items',
    label: 'Action Items',
    icon: 'task_alt',
    desc: 'Extracts tasks, deadlines, and responsibilities.',
  },
]

const lengths: SummaryLength[] = ['Short', 'Medium', 'Long']

interface ConfigureState {
  documentId: string
  format: SummaryFormat
  detail: DetailLevel
}

export function ConfigureSummary(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const state = location.state as ConfigureState | null
  const documentId = state?.documentId ?? searchParams.get('doc') ?? ''
  const format: SummaryFormat = state?.format ?? 'bullets'
  const detail: DetailLevel = state?.detail ?? 'concise'

  const [length, setLength] = useState<SummaryLength>('Short')
  const [style, setStyle] = useState<SummaryStyle>('executive')
  const [includePoints, setIncludePoints] = useState(true)
  const [includeQuotes, setIncludeQuotes] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [text, setText] = useState<ExtractedTextData | null>(null)
  const [textError, setTextError] = useState<string | null>(null)

  useEffect(() => {
    if (!documentId) return
    let alive = true
    api
      .extractedText(documentId)
      .then((t) => {
        if (alive) setText(t)
      })
      .catch((e) => {
        if (alive)
          setTextError(
            e instanceof Error ? e.message : 'Failed to load extracted text',
          )
      })
    return () => {
      alive = false
    }
  }, [documentId])

  if (!documentId) return <Navigate to="/" replace />

  const generate = async (): Promise<void> => {
    setGenerating(true)
    setError(null)
    try {
      const { job } = await api.createSummary({
        document_id: documentId,
        length,
        style,
        format,
        detail_level: detail,
        include_key_points: includePoints,
        include_quotes: includeQuotes,
      })
      navigate('/processing', { state: { jobId: job.id } })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start generation')
      setGenerating(false)
    }
  }

  const currentText = text && text.document_id === documentId ? text : null

  return (
    <div className="mx-auto max-w-[800px] px-4 md:px-8 py-8 md:py-12">
      <div className="border border-line bg-surface-lowest">
        <header className="px-6 md:px-8 py-7 border-b border-line">
          <p className="eyebrow text-accent">Composition</p>
          <h1 className="font-display text-3xl md:text-[36px] font-semibold tracking-tight text-ink mt-2">
            Create your summary
          </h1>
          <p className="mt-1.5 text-[15px] text-ink-variant">
            Choose how you want TheSummarist to understand this document.
          </p>
        </header>

        <section className="px-6 md:px-8 py-7 border-b border-line">
          <div className="flex items-center justify-between gap-3 mb-4">
            <h2 className="font-display text-xl font-semibold text-ink">Extracted Text</h2>
            {currentText && (
              <span className="font-mono text-[11px] text-ink-muted whitespace-nowrap">
                {(currentText.words ?? 0).toLocaleString()} words
                {currentText.pages != null ? ` · ${currentText.pages} pages` : ''}
                {currentText.language ? ` · ${currentText.language}` : ''}
              </span>
            )}
          </div>
          {textError && !currentText ? (
            <p className="border border-line bg-surface-low p-4 text-[13px] text-error">
              {textError}
            </p>
          ) : !currentText ? (
            <div className="border border-line bg-surface-low p-8 grid place-items-center">
              <Icon name="sync" className="text-[22px] text-accent animate-spin" />
            </div>
          ) : (
            <div className="border border-line bg-surface-lowest max-h-[340px] overflow-y-auto px-6 md:px-8 py-5">
              <p className="text-[13px] font-medium text-ink-variant truncate mb-4">
                {currentText.file_name}
              </p>
              <article className="max-w-[640px]">
                <h3 className="font-display text-lg font-semibold tracking-tight text-ink leading-snug">
                  {currentText.title}
                </h3>
                <div className="rule-thick-thin my-4" />
                <div className="space-y-6">
                  {currentText.body.map((section, si) => (
                    <div key={`${section.heading}-${si}`}>
                      <h4 className="font-display text-[15px] font-semibold text-ink mb-3">
                        {section.heading}
                      </h4>
                      <div className="space-y-3.5">
                        {section.paragraphs.map((p, i) => (
                          <p
                            key={i}
                            className="text-[14px] leading-[1.7] text-ink-variant"
                          >
                            {p}
                          </p>
                        ))}
                        {section.bullets && section.bullets.length > 0 && (
                          <ul className="space-y-2.5 pl-1">
                            {section.bullets.map((b, i) => (
                              <li key={i} className="flex items-start gap-2.5">
                                <span className="font-mono text-[11px] text-accent mt-[4px] shrink-0">
                                  §
                                </span>
                                <span className="text-[14px] leading-[1.65] text-ink-variant">
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
          )}
        </section>

        <div className="px-6 md:px-8 py-7">
          <section className="mb-9">
            <h2 className="font-display text-xl font-semibold text-ink mb-4">Length</h2>
            <div className="inline-flex border border-line-strong">
              {lengths.map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLength(l)}
                  className={`px-6 py-2 text-[13px] font-medium transition-colors ${
                    length === l
                      ? 'bg-accent text-surface-lowest'
                      : 'text-ink-variant hover:text-ink hover:bg-surface-low'
                  } ${l !== 'Short' ? 'border-l border-line-strong' : ''}`}
                >
                  {l}
                </button>
              ))}
            </div>
          </section>

          <section className="mb-9">
            <h2 className="font-display text-xl font-semibold text-ink mb-4">Style</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {styles.map((s) => (
                <button
                  key={s.value}
                  type="button"
                  onClick={() => setStyle(s.value)}
                  className={`text-left rounded-[3px] border p-4 transition-colors ${
                    style === s.value
                      ? 'border-accent bg-accent-tint'
                      : 'border-line bg-surface-lowest hover:border-line-strong'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <Icon name={s.icon} className="text-accent text-[22px]" />
                    <span
                      className={`w-4 h-4 rounded-full border-2 ${
                        style === s.value ? 'border-accent border-[5px]' : 'border-line-strong'
                      }`}
                    />
                  </div>
                  <h3 className="mt-3 text-[13.5px] font-medium text-ink">{s.label}</h3>
                  <p className="mt-1 text-[12.5px] text-ink-variant leading-snug">{s.desc}</p>
                </button>
              ))}
            </div>
          </section>

          <section className="pt-7 border-t border-line">
            <h2 className="font-display text-xl font-semibold text-ink mb-4">
              Additional Options
            </h2>
            <div className="border border-line bg-surface-low p-5 space-y-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="text-[14px] font-medium text-ink">Include key points</div>
                  <div className="text-[12.5px] text-ink-variant">
                    Append a concise list to the end.
                  </div>
                </div>
                <Toggle checked={includePoints} onChange={setIncludePoints} />
              </div>
              <div className="h-px bg-line w-full" />
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="text-[14px] font-medium text-ink">
                    Include important quotes
                  </div>
                  <div className="text-[12.5px] text-ink-variant">
                    Extract verbatim significant statements.
                  </div>
                </div>
                <Toggle checked={includeQuotes} onChange={setIncludeQuotes} />
              </div>
            </div>
          </section>

          {error && <p className="mt-4 text-[13px] text-error">{error}</p>}
        </div>

        <footer className="px-6 md:px-8 py-5 border-t border-line flex justify-end items-center gap-3">
          <Button variant="ghost" onClick={() => navigate('/summaries')}>
            Cancel
          </Button>
          <Button icon="auto_awesome" disabled={generating} onClick={() => void generate()}>
            {generating ? 'Starting…' : 'Generate Summary'}
          </Button>
        </footer>
      </div>
    </div>
  )
}

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean
  onChange: (v: boolean) => void
}): JSX.Element {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${
        checked ? 'bg-accent' : 'bg-surface-container'
      }`}
    >
      <span
        className={`inline-block h-5 w-5 transform rounded-full bg-surface-lowest shadow-card transition-transform ${
          checked ? 'translate-x-[22px]' : 'translate-x-0.5'
        }`}
      />
    </button>
  )
}
