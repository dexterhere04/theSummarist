import { useEffect, useState } from 'react'
import type { JSX } from 'react'
import { api } from '../lib/api'
import type { SummaryLength, SummaryStyle, UserSettings as SettingsData } from '../lib/types'
import { Icon } from '../components/Icon'

const lengths: SummaryLength[] = ['Short', 'Medium', 'Long']

const styleOptions: { value: SummaryStyle; label: string }[] = [
  { value: 'executive', label: 'Executive Summary' },
  { value: 'key_points', label: 'Key Points' },
  { value: 'detailed', label: 'Detailed Summary' },
  { value: 'study_notes', label: 'Study Notes' },
  { value: 'action_items', label: 'Action Items' },
]

export function Settings(): JSX.Element {
  const [settings, setSettings] = useState<SettingsData | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.settings().then(setSettings).catch(() => setSettings(null))
  }, [])

  const save = async (patch: Partial<SettingsData>): Promise<void> => {
    if (!settings) return
    const next = { ...settings, ...patch }
    setSettings(next)
    try {
      const updated = await api.patchSettings(patch)
      setSettings(updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 1500)
    } catch {
      /* keep optimistic UI */
    }
  }

  if (!settings) {
    return (
      <div className="py-24 text-center">
        <Icon name="sync" className="text-[32px] text-accent animate-spin" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl px-4 md:px-8 py-10 md:py-12">
      <p className="eyebrow text-accent">Account</p>
      <h1 className="font-display text-3xl md:text-[40px] font-semibold tracking-tight text-ink mt-2">
        Settings
      </h1>
      <div className="rule-thick-thin mt-5 mb-8" />

      <div className="border border-line bg-surface-lowest divide-y divide-line">
        <Row label="Default summary length" hint="Preselected on the configure page.">
          <div className="inline-flex border border-line-strong">
            {lengths.map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => void save({ default_length: l })}
                className={`px-4 py-1.5 text-[13px] font-medium transition-colors ${
                  settings.default_length === l
                    ? 'bg-accent text-surface-lowest'
                    : 'text-ink-variant hover:bg-surface-low'
                } ${l !== 'Short' ? 'border-l border-line-strong' : ''}`}
              >
                {l}
              </button>
            ))}
          </div>
        </Row>

        <Row label="Default style" hint="Applied when generating summaries.">
          <select
            value={settings.default_style}
            onChange={(e) => void save({ default_style: e.target.value as SummaryStyle })}
            className="h-9 px-3 rounded-[3px] border border-line bg-surface-lowest text-[13px] text-ink focus:outline-none focus:border-accent"
          >
            {styleOptions.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </Row>

        <Row label="Language" hint="Extraction and summary language.">
          <input
            type="text"
            value={settings.language}
            readOnly
            className="h-9 w-28 px-3 rounded-[3px] border border-line bg-surface-low text-[13px] font-mono text-ink-muted"
          />
        </Row>

        <Row label="Theme" hint="Interface appearance.">
          <div className="inline-flex border border-line-strong">
            {(['light', 'dark'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => void save({ theme: t })}
                className={`px-4 py-1.5 text-[13px] font-medium capitalize transition-colors ${
                  settings.theme === t
                    ? 'bg-accent text-surface-lowest'
                    : 'text-ink-variant hover:bg-surface-low'
                } ${t !== 'light' ? 'border-l border-line-strong' : ''}`}
              >
                {t}
              </button>
            ))}
          </div>
        </Row>
      </div>

      <p
        className={`mt-4 text-[13px] text-ok flex items-center gap-1.5 transition-opacity ${
          saved ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <Icon name="check" filled className="text-[16px]" /> Saved
      </p>
    </div>
  )
}

function Row({
  label,
  hint,
  children,
}: {
  label: string
  hint: string
  children: React.ReactNode
}): JSX.Element {
  return (
    <div className="flex items-center justify-between gap-6 px-6 py-5">
      <div>
        <div className="text-[14.5px] font-medium text-ink">{label}</div>
        <div className="text-[12.5px] text-ink-variant mt-0.5">{hint}</div>
      </div>
      {children}
    </div>
  )
}
