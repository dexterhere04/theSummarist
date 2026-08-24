import { useState } from 'react'
import type { KeyboardEvent, JSX } from 'react'
import { useNavigate } from 'react-router-dom'
import { Icon } from './Icon'

export function TopBar(): JSX.Element {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')

  const search = (e: KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === 'Enter') navigate(`/summaries?q=${encodeURIComponent(query.trim())}`)
  }

  return (
    <header className="flex items-center justify-between gap-4 h-[68px] px-4 md:px-6 border-b border-line bg-surface/80 backdrop-blur-md sticky top-0 z-30">
      <div className="flex items-center gap-3 min-w-0">
        <div className="md:hidden flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-[4px] bg-accent text-surface-lowest grid place-items-center">
            <Icon name="summarize" className="text-[15px]" />
          </div>
          <span className="font-display font-semibold text-[15px] text-ink">
            The<span className="italic">Summarist</span>
          </span>
        </div>
        <div className="relative hidden sm:block w-72">
          <Icon
            name="search"
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-ink-muted"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={search}
            placeholder="Search the library…"
            className="w-full h-9 pl-9 pr-3 rounded-[4px] border border-line bg-surface-lowest/70 text-sm placeholder:text-ink-muted focus:outline-none focus:border-accent focus:bg-surface-lowest transition-colors"
          />
        </div>
      </div>
    </header>
  )
}
