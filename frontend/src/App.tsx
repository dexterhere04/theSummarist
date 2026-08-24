import { useEffect, useState } from 'react'
import type { JSX } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ensureSession } from './lib/api'
import { AppShell } from './components/AppShell'
import { ConfigureSummary } from './pages/ConfigureSummary'
import { Dashboard } from './pages/Dashboard'
import { ExtractedText } from './pages/ExtractedText'
import { MySummaries } from './pages/MySummaries'
import { Processing } from './pages/Processing'
import { Profile } from './pages/Profile'
import { RecentDocuments } from './pages/RecentDocuments'
import { Settings } from './pages/Settings'
import { Summary } from './pages/Summary'

export default function App(): JSX.Element {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    ensureSession()
      .catch(() => undefined)
      .finally(() => setReady(true))
  }, [])

  if (!ready) {
    return (
      <div className="min-h-screen grid place-items-center bg-background">
        <span className="font-display text-3xl text-accent animate-pulse">¶</span>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/summaries" element={<MySummaries />} />
          <Route path="/document/:id" element={<ExtractedText />} />
          <Route path="/configure" element={<ConfigureSummary />} />
          <Route path="/processing" element={<Processing />} />
          <Route path="/summary/:id" element={<Summary />} />
          <Route path="/recent" element={<RecentDocuments />} />
          <Route
            path="/favorites"
            element={<MySummaries key="favorites" initialTab="favorites" />}
          />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}
