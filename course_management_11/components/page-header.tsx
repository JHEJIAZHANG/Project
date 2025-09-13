import type React from "react"
interface PageHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
}

export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <header className="flex items-center justify-between mb-6 lg:mb-12">
      <div>
        <h1 className="text-2xl lg:text-4xl xl:text-5xl font-bold text-foreground text-balance">{title}</h1>
        {subtitle && <p className="text-sm lg:text-lg xl:text-xl text-muted-foreground mt-1 lg:mt-3">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </header>
  )
}
