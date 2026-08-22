import type { JSX } from 'react'
import { Icon } from '../components/Icon'

const steps = [
  {
    state: 'done' as const,
    title: 'Document uploaded',
    desc: 'File securely stored and verified.',
  },
  {
    state: 'done' as const,
    title: 'Extracting text',
    desc: 'OCR and layout parsing completed.',
  },
  {
    state: 'active' as const,
    title: 'Understanding document',
    desc: 'Applying semantic analysis and identifying key entities…',
  },
  {
    state: 'pending' as const,
    title: 'Preparing summary',
    desc: 'Waiting for preceding steps.',
  },
]

export function Processing(): JSX.Element {
  return (
    <div className="mx-auto max-w-[900px] px-4 md:px-8 py-8 md:py-12">
      <div className="text-center mb-10">
        <p className="eyebrow text-accent">In press</p>
        <h1 className="font-display text-3xl md:text-[38px] font-semibold tracking-tight text-ink mt-2">
          Processing Document
        </h1>
        <p className="mt-1.5 text-[15px] text-ink-variant">
          Our AI is analyzing your file to generate intelligent insights.
        </p>
      </div>

      <div className="border border-line bg-surface-lowest p-5 mb-8">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-[4px] bg-surface-low text-accent grid place-items-center border border-line">
            <Icon name="description" className="text-[24px]" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="font-medium text-[15px] text-ink truncate">
              Q4_Financial_Report_2023_Final_Draft.pdf
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="font-mono text-[9.5px] font-semibold tracking-[0.14em] text-ink-variant border border-line-strong/50 px-1.5 py-[3px] rounded-[3px]">
                PDF
              </span>
              <span className="text-[12.5px] text-ink-variant">4.2 MB</span>
              <span className="text-line text-[10px]">·</span>
              <span className="text-[12.5px] text-ink-variant">
                Uploaded 2 mins ago
              </span>
            </div>
          </div>
          <button
            type="button"
            title="Cancel processing"
            className="w-9 h-9 rounded-[3px] grid place-items-center text-ink-variant hover:text-error hover:bg-error-soft transition-colors"
          >
            <Icon name="close" className="text-[20px]" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div className="md:col-span-5 border border-line bg-surface-lowest p-8 flex flex-col items-center justify-center min-h-[280px]">
          <div className="relative w-40 h-40 flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border border-line" />
            <div className="absolute inset-0 rounded-full border border-transparent border-t-accent animate-[spin_2.4s_linear_infinite]" />
            <div className="absolute inset-5 rounded-full border border-line/70" />
            <div className="absolute inset-5 rounded-full border border-transparent border-b-accent animate-[spin_3.8s_linear_infinite_reverse]" />
            <div className="absolute inset-10 rounded-full border border-line/50" />
            <span className="font-display text-3xl text-accent leading-none">¶</span>
          </div>
          <p className="mt-7 font-mono text-[11px] text-accent tracking-[0.2em] uppercase">
            Analyzing Context…
          </p>
        </div>

        <div className="md:col-span-7 border border-line bg-surface-lowest p-6 md:p-8">
          <h3 className="font-display text-xl font-semibold text-ink mb-7">
            Processing Status
          </h3>
          <div className="relative">
            <div className="absolute left-[19px] top-6 bottom-6 w-px bg-line" />
            <ul className="space-y-6 relative">
              {steps.map((step) => (
                <li key={step.title} className="flex items-start gap-4">
                  <div className="relative bg-surface-lowest py-1 z-10">
                    {step.state === 'active' ? (
                      <div className="w-10 h-10 rounded-[3px] bg-accent grid place-items-center">
                        <Icon
                          name="sync"
                          className="text-surface-lowest text-[20px] animate-[spin_3s_linear_infinite]"
                        />
                      </div>
                    ) : step.state === 'done' ? (
                      <div className="w-10 h-10 rounded-[3px] bg-accent-soft grid place-items-center border border-accent/30">
                        <Icon
                          name="check"
                          filled
                          className="text-accent text-[20px]"
                        />
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-[3px] bg-surface-lowest grid place-items-center border border-line">
                        <span className="font-mono text-[13px] text-ink-muted">
                          ¶
                        </span>
                      </div>
                    )}
                  </div>
                  <div className={`py-2 ${step.state === 'pending' ? 'opacity-45' : ''}`}>
                    <h4
                      className={`text-[15px] font-semibold ${
                        step.state === 'active' ? 'text-accent' : 'text-ink'
                      }`}
                    >
                      {step.title}
                    </h4>
                    <p
                      className={`text-[13px] ${
                        step.state === 'active'
                          ? 'text-accent/90'
                          : 'text-ink-variant'
                      }`}
                    >
                      {step.desc}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-9">
        <button
          type="button"
          className="inline-flex items-center gap-1.5 text-[13px] font-medium text-accent underline-offset-4 hover:underline"
        >
          <Icon name="open_in_new" className="text-[16px]" />
          Run in background
        </button>
      </div>
    </div>
  )
}
