import type { JSX } from 'react'
import { NavLink } from 'react-router-dom'
import { Icon } from './Icon'

const items = [
  { to: '/summaries', label: 'Summaries', icon: 'folder_open' },
  { to: '/recent', label: 'Recent', icon: 'history' },
  { to: '/favorites', label: 'Favorites', icon: 'star' },
  { to: '/profile', label: 'Profile', icon: 'account_circle' },
]

export function BottomNav(): JSX.Element {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-surface/92 backdrop-blur-md border-t border-line flex items-stretch justify-around h-16 pb-[env(safe-area-inset-bottom)]">
      {items.map(({ to, label, icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/summaries'}
          className={({ isActive }) =>
            `flex-1 flex flex-col items-center justify-center gap-1 text-[10.5px] font-medium transition-colors relative ${
              isActive ? 'text-accent-strong' : 'text-ink-variant'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <span
                className={`absolute top-0 left-1/2 -translate-x-1/2 w-6 h-[2px] bg-accent transition-opacity ${
                  isActive ? 'opacity-100' : 'opacity-0'
                }`}
              />
              <Icon name={icon} filled={isActive} className="text-[22px]" />
              {label}
            </>
          )}
        </NavLink>
      ))}
    </nav>
  )
}
