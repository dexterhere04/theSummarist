import { useEffect, useState } from 'react'
import type { JSX } from 'react'
import { NavLink } from 'react-router-dom'
import { api } from '../lib/api'
import type { User } from '../lib/types'
import { Icon } from './Icon'

const primaryNav = [
  { to: '/summaries', label: 'My Summaries', icon: 'folder_open', end: false },
  { to: '/recent', label: 'Recent Documents', icon: 'history', end: false },
  { to: '/favorites', label: 'Favorites', icon: 'star', end: false },
]

const secondaryNav = [
  { to: '/settings', label: 'Settings', icon: 'settings', end: false },
  { to: '/profile', label: 'Profile', icon: 'account_circle', end: false },
]

function NavItem({
  to,
  label,
  icon,
  end,
}: {
  to: string
  label: string
  icon: string
  end: boolean
}): JSX.Element {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `group flex items-center gap-3 rounded-r px-3 py-2 text-[14px] transition-colors border-l-2 ${
          isActive
            ? 'border-accent bg-accent-tint/70 text-accent-strong'
            : 'border-transparent text-ink-variant hover:bg-surface-low hover:text-ink'
        }`
      }
    >
      {({ isActive }) => (
        <>
          <Icon
            name={icon}
            filled={isActive}
            className={`text-[19px] ${isActive ? 'text-accent' : 'text-ink-muted group-hover:text-ink-variant'}`}
          />
          <span className="truncate">{label}</span>
        </>
      )}
    </NavLink>
  )
}

export function Sidebar(): JSX.Element {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null))
  }, [])

  return (
    <aside className="hidden md:flex flex-col w-[248px] shrink-0 border-r border-line bg-surface h-screen sticky top-0">
      <div className="px-5 h-[68px] border-b border-line flex items-center gap-3">
        <div className="w-9 h-9 rounded-[4px] bg-accent text-surface-lowest grid place-items-center shrink-0">
          <Icon name="summarize" className="text-[19px]" />
        </div>
        <div className="leading-none">
          <div className="font-display font-semibold text-[16px] tracking-tight text-ink">
            The<span className="italic">Summarist</span>
          </div>
          <div className="font-mono text-[9.5px] tracking-[0.18em] uppercase text-ink-muted mt-1.5">
            Fine-press reader
          </div>
        </div>
      </div>

      <div className="px-3 pt-4">
        <NavLink
          to="/"
          end
          className="flex items-center justify-center gap-2 h-10 rounded bg-accent text-surface-lowest text-sm font-medium hover:bg-accent-strong transition-colors"
        >
          <Icon name="add" className="text-[18px]" />
          New Summary
        </NavLink>
      </div>

      <nav className="flex-1 px-3 py-5 space-y-0.5 overflow-y-auto">
        <div className="px-3 pb-2 eyebrow text-ink-muted">Library</div>
        {primaryNav.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
        <div className="pt-5 px-3 pb-2 eyebrow text-ink-muted">Account</div>
        {secondaryNav.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>

      <div className="p-3 border-t border-line">
        <div className="flex items-center gap-3 rounded px-2 py-2">
          <div className="w-9 h-9 rounded-[4px] bg-surface-container text-accent grid place-items-center font-display font-semibold text-sm">
            {user?.avatar_initials ?? '·'}
          </div>
          <div className="min-w-0 leading-tight">
            <div className="text-[13.5px] font-medium truncate">{user?.name ?? '…'}</div>
            <div className="font-mono text-[11px] text-ink-muted truncate">
              {user?.email ?? ''}
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
