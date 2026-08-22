import type { JSX } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { ConfigureSummary } from './pages/ConfigureSummary'
import { Dashboard } from './pages/Dashboard'
import { EmptyState } from './pages/EmptyState'
import { ExtractedText } from './pages/ExtractedText'
import { MySummaries } from './pages/MySummaries'
import { Processing } from './pages/Processing'
import { Summary } from './pages/Summary'

export default function App(): JSX.Element {
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
          <Route path="/recent" element={<EmptyState label="Recent Documents" />} />
          <Route path="/favorites" element={<EmptyState label="Favorites" />} />
          <Route path="/settings" element={<EmptyState label="Settings" />} />
          <Route path="/profile" element={<EmptyState label="Profile" />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}
