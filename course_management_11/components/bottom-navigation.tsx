"use client"

import { HomeIcon, BookIcon, ClipboardIcon, DocumentIcon, UserIcon } from "./icons"
import { cn } from "@/lib/utils"

interface BottomNavigationProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export function BottomNavigation({ activeTab, onTabChange }: BottomNavigationProps) {
  const tabs = [
    { id: "home", label: "首頁", icon: HomeIcon },
    { id: "courses", label: "課程", icon: BookIcon },
    { id: "tasks", label: "待辦", icon: ClipboardIcon },
    { id: "notes", label: "筆記", icon: DocumentIcon },
    { id: "profile", label: "我的", icon: UserIcon },
  ]

  return (
    /* hide bottom navigation on desktop with lg:hidden */
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-border lg:hidden">
      <div className="flex items-center justify-around py-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={cn(
                "flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors",
                isActive ? "text-white bg-primary" : "text-muted-foreground hover:text-foreground hover:bg-muted/50",
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{tab.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
