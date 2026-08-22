import { useState } from 'react'
import type { JSX } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'

const styles = [
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

const lengths = ['Short', 'Medium', 'Long']

export function ConfigureSummary(): JSX.Element {
  const navigate = useNavigate()
  const [length, setLength] = useState('Short')
  const [style, setStyle] = useState('executive')
  const [includePoints, setIncludePoints] = useState(true)
  const [includeQuotes, setIncludeQuotes] = useState(false)

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

        <div className="px-6 md:px-8 py-7">
          <section className="mb-9">
            <h2 className="font-display text-xl font-semibold text-ink mb-4">
              Length
            </h2>
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
            <h2 className="font-display text-xl font-semibold text-ink mb-4">
              Style
            </h2>
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
                        style === s.value
                          ? 'border-accent border-[5px]'
                          : 'border-line-strong'
                      }`}
                    />
                  </div>
                  <h3 className="mt-3 text-[13.5px] font-medium text-ink">
                    {s.label}
                  </h3>
                  <p className="mt-1 text-[12.5px] text-ink-variant leading-snug">
                    {s.desc}
                  </p>
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
                  <div className="text-[14px] font-medium text-ink">
                    Include key points
                  </div>
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
        </div>

        <footer className="px-6 md:px-8 py-5 border-t border-line flex justify-end items-center gap-3">
          <Button variant="ghost" onClick={() => navigate('/summaries')}>
            Cancel
          </Button>
          <Button
            icon="auto_awesome"
            onClick={() => navigate('/summary/annual-financial-report')}
          >
            Generate Summary
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
