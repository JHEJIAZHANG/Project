"use client"

import { HomeIcon, BookIcon, ClipboardIcon, DocumentIcon, UserIcon } from "./icons"
import { cn } from "@/lib/utils"
import { useState, useEffect } from "react"

interface SidebarNavigationProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export function SidebarNavigation({ activeTab, onTabChange }: SidebarNavigationProps) {
  const [isCollapsed, setIsCollapsed] = useState(true)
  const [showText, setShowText] = useState(false)

  useEffect(() => {
    document.documentElement.style.setProperty("--sidebar-width", isCollapsed ? "4rem" : "16rem")
  }, [isCollapsed])

  const handleMouseEnter = () => {
    setIsCollapsed(false)
    setTimeout(() => {
      setShowText(true)
    }, 200)
  }

  const handleMouseLeave = () => {
    setShowText(false)
    setIsCollapsed(true)
  }

  const tabs = [
    { id: "home", label: "首頁", icon: HomeIcon },
    { id: "courses", label: "課程", icon: BookIcon },
    { id: "tasks", label: "待辦", icon: ClipboardIcon },
    { id: "notes", label: "筆記", icon: DocumentIcon },
    { id: "profile", label: "我的", icon: UserIcon },
  ]

  return (
    <nav
      className={cn(
        "hidden lg:flex lg:flex-col lg:fixed lg:left-0 lg:top-0 lg:h-full lg:bg-white lg:border-r lg:border-border lg:z-30 transition-all duration-200",
        isCollapsed ? "lg:w-16" : "lg:w-64",
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div
        className={cn(
          "border-b border-border flex items-center h-16",
          isCollapsed ? "justify-center" : "justify-start px-6",
        )}
      >
        {!isCollapsed && showText && <h1 className="text-xl font-bold text-foreground">課程管理系統</h1>}
      </div>
      <div className="flex-1 p-4">
        <div className="space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={cn(
                  "w-full flex items-center rounded-lg transition-colors text-left h-12",
                  isCollapsed
                    ? isActive
                      ? "text-white bg-primary justify-center"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50 justify-center"
                    : isActive
                      ? "text-white bg-primary"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50",
                )}
                title={isCollapsed ? tab.label : undefined}
              >
                <div
                  className={cn(
                    "flex items-center justify-center flex-shrink-0",
                    isCollapsed ? "w-12 h-12" : "w-12 h-12",
                  )}
                >
                  <Icon className="w-5 h-5" />
                </div>
                {!isCollapsed && showText && <span className="font-medium ml-1">{tab.label}</span>}
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
