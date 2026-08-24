import { useEffect, useState } from 'react'
import type { JSX } from 'react'
import { api } from '../lib/api'
import type { User as UserData } from '../lib/types'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'

export function Profile(): JSX.Element {
  const [user, setUser] = useState<UserData | null>(null)
  const [name, setName] = useState('')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.me().then((u) => {
      setUser(u)
      setName(u.name)
    })
  }, [])

  const saveName = async (): Promise<void> => {
    setError(null)
    try {
      const updated = await api.patchMe({ name })
      setUser(updated)
      setName(updated.name)
      setSaved(true)
      setTimeout(() => setSaved(false), 1500)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Update failed')
    }
  }

  if (!user) {
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
        Profile
      </h1>
      <div className="rule-thick-thin mt-5 mb-8" />

      <div className="border border-line bg-surface-lowest p-6">
        <div className="flex items-center gap-4 mb-7">
          <div className="w-14 h-14 rounded-[4px] bg-surface-container text-accent grid place-items-center font-display font-semibold text-xl">
            {user.avatar_initials}
          </div>
          <div className="leading-tight">
            <div className="font-display font-semibold text-[18px] text-ink">{user.name}</div>
            <div className="font-mono text-[12px] text-ink-muted">{user.email}</div>
          </div>
          <span className="ml-auto font-mono text-[9.5px] uppercase tracking-[0.14em] text-accent border border-accent/30 bg-accent-soft px-2 py-1 rounded-[3px]">
            {user.plan} plan
          </span>
        </div>

        <label className="eyebrow text-ink-muted block mb-2">Display name</label>
        <div className="flex gap-3">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="flex-1 h-10 px-3 rounded-[3px] border border-line bg-surface-lowest text-[14px] text-ink focus:outline-none focus:border-accent"
          />
          <Button onClick={() => void saveName()} disabled={!name.trim() || name === user.name}>
            Save
          </Button>
        </div>
        {error && <p className="mt-3 text-[13px] text-error">{error}</p>}
        <p
          className={`mt-3 text-[13px] text-ok flex items-center gap-1.5 transition-opacity ${
            saved ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <Icon name="check" filled className="text-[16px]" /> Saved
        </p>

        <div className="mt-7 pt-5 border-t border-line">
          <p className="font-mono text-[11px] text-ink-muted">
            Member since {new Date(user.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  )
}
