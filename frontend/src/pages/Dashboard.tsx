import { useEffect, useRef, useState } from 'react'
import type { CSSProperties, DragEvent, JSX } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import type { SummaryItem } from '../lib/types'
import { Button } from '../components/Button'
import { FormatBadge } from '../components/FormatBadge'
import { Icon } from '../components/Icon'

const delay = (i: number): CSSProperties => ({ ['--reveal-delay' as string]: `${i * 90}ms` })

export function Dashboard(): JSX.Element {
  const navigate = useNavigate()
  const fileInput = useRef<HTMLInputElement>(null)
  const [recent, setRecent] = useState<SummaryItem[]>([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listSummaries({ tab: 'recent', per_page: 3 })
      .then((page) => setRecent(page.items))
      .catch(() => setRecent([]))
  }, [])

  const upload = async (file: File | undefined | null): Promise<void> => {
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      const { job } = await api.upload(file, false)
      navigate('/processing', { state: { jobId: job.id } })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed')
      setUploading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 md:px-8 py-10 md:py-14">
      <input
        ref={fileInput}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.pptx,.txt"
        className="hidden"
        onChange={(e) => {
          void upload(e.target.files?.[0])
          e.target.value = ''
        }}
      />

      <section className="mb-12 md:text-left text-center">
        <div className="flex flex-col md:flex-row md:items-end items-center justify-between gap-6">
          <div>
            <h1
              className="font-display text-4xl md:text-[52px] font-semibold tracking-tight text-ink leading-[1.02] mt-3 reveal"
              style={delay(1)}
            >
              Welcome to
              <br />
              <span className="italic text-accent-strong">The Summarist</span>
            </h1>
          </div>

          <div
            className="flex items-center gap-4 md:gap-5 shrink-0 reveal"
            style={delay(1)}
          >
            <div className="relative max-w-[230px] rounded-lg border border-line bg-surface-lowest px-4 py-3 text-left">
              <p className="font-serif text-[14px] italic leading-snug text-ink">
                <b>Hi, I’m the Summarist, your guide for summaries.</b>
              </p>
              <span className="absolute top-1/2 -right-[7px] -translate-y-1/2 h-3.5 w-3.5 rotate-45 border-t border-r border-line bg-surface-lowest" />
            </div>
            <img
              src="/mascot.svg"
              alt="TheSummarist inkwell mascot"
              className="-rotate-6 w-24 md:w-36"
            />
          </div>
        </div>
        <p
          className="mt-4 text-[17px] text-ink-variant max-w-xl leading-relaxed reveal"
          style={delay(2)}
        >
          Turn your documents into something worth reading. Upload a file and
          let the press do the heavy lifting.
        </p>
        <div
          className="mt-7 flex flex-wrap gap-3 md:justify-start justify-center reveal"
          style={delay(3)}
        >
          <Button icon="add" onClick={() => fileInput.current?.click()}>
            New Summary
          </Button>
          <Link to="/summaries">
            <Button variant="secondary" icon="grid_view">
              Browse the Library
            </Button>
          </Link>
        </div>
      </section>

      <section className="mb-12 reveal" style={delay(4)}>
        <button
          type="button"
          disabled={uploading}
          onClick={() => fileInput.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e: DragEvent<HTMLButtonElement>) => {
            e.preventDefault()
            void upload(e.dataTransfer.files?.[0])
          }}
          className="w-full block group cursor-pointer disabled:opacity-60"
        >
          <div className="relative border border-dashed border-line-strong bg-surface-lowest hover:border-accent transition-colors p-10 md:p-14 flex flex-col items-center text-center">
            <span className="absolute top-3 left-3 w-3 h-3 border-t border-l border-ink/40" />
            <span className="absolute top-3 right-3 w-3 h-3 border-t border-r border-ink/40" />
            <span className="absolute bottom-3 left-3 w-3 h-3 border-b border-l border-ink/40" />
            <span className="absolute bottom-3 right-3 w-3 h-3 border-b border-r border-ink/40" />
            <div className="w-16 h-16 rounded-[4px] bg-surface-low text-accent grid place-items-center mb-6 group-hover:bg-accent group-hover:text-surface-lowest transition-colors">
              <Icon name={uploading ? 'sync' : 'cloud_upload'} className={`text-[26px] ${uploading ? 'animate-spin' : ''}`} />
            </div>
            <h2 className="font-display text-2xl font-semibold text-ink">
              {uploading ? 'Uploading…' : 'Drop a document here'}
            </h2>
            <p className="mt-1.5 text-[15px] text-ink-variant">
              PDF, PNG, JPG or JPEG — up to 50 MB
            </p>
            <span className="mt-6 inline-flex h-9 items-center px-5 text-[13px] font-medium tracking-[0.02em] rounded border border-line-strong text-ink group-hover:border-accent group-hover:text-accent transition-colors">
              Choose File
            </span>
          </div>
        </button>
        {error && (
          <p className="mt-3 text-[13px] text-error text-center">{error}</p>
        )}
      </section>

      <section className="reveal" style={delay(5)}>
        <div className="flex items-end justify-between mb-1">
          <h2 className="font-display text-xl font-semibold text-ink">
            Recent summaries
          </h2>
          <Link
            to="/summaries"
            className="text-[13px] font-medium text-accent underline-offset-4 hover:underline"
          >
            View all
          </Link>
        </div>
        <div className="rule-thick-thin mt-2 mb-2" />

        {recent.length === 0 ? (
          <p className="py-8 text-[14px] text-ink-muted text-center">
            No summaries yet — upload a document to get started.
          </p>
        ) : (
          <div className="flex flex-col">
            {recent.map((s, i) => (
              <Link
                key={s.id}
                to={`/summary/${s.id}`}
                className={`group flex items-center gap-4 px-2 py-4 hover:bg-surface-lowest transition-colors ${
                  i < recent.length - 1 ? 'border-b border-line' : ''
                }`}
              >
                <span className="font-mono text-[12px] text-ink-muted w-6 shrink-0">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <FormatBadge format={s.format} />
                <div className="flex-1 min-w-0">
                  <h3 className="text-[15.5px] font-medium text-ink truncate group-hover:text-accent transition-colors">
                    {s.title}
                  </h3>
                  <p className="text-[13.5px] text-ink-variant truncate">
                    {s.excerpt || s.tldr}
                  </p>
                </div>
                <span className="font-mono text-[11.5px] text-ink-muted whitespace-nowrap hidden sm:block">
                  {s.date}
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
