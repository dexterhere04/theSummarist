import type { JSX, ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { BottomNav } from './BottomNav'

export function AppShell({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <Sidebar />
        <div className="flex-1 min-w-0 flex flex-col min-h-screen">
          <TopBar />
          <main className="flex-1 pb-24 md:pb-12">{children}</main>
        </div>
      </div>
      <BottomNav />
    </div>
  )
}
