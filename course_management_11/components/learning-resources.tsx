"use client"

import type React from "react"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { Assignment, Course } from "@/types/course"

interface LearningResource {
  title: string
  url: string
  type: "youtube" | "website" | "documentation"
  description: string
}

interface LearningResourcesProps {
  assignment?: Assignment
  course?: Course
  searchQuery?: string
}

const extractYouTubeInfo = (url: string) => {
  const youtubeRegex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/
  const match = url.match(youtubeRegex)
  if (match) {
    const videoId = match[1]
    return {
      title: `YouTube 影片 - ${videoId}`,
      description: "從 YouTube 拖曳新增的學習資源",
      type: "youtube" as const,
    }
  }
  return null
}

const extractWebsiteInfo = (url: string) => {
  try {
    const urlObj = new URL(url)
    return {
      title: `網站資源 - ${urlObj.hostname}`,
      description: `從 ${urlObj.hostname} 新增的學習資源`,
      type: "website" as const,
    }
  } catch {
    return {
      title: "網站資源",
      description: "新增的學習資源",
      type: "website" as const,
    }
  }
}

// 模擬學習資源數據庫
const getResourcesByKeywords = (keywords: string[]): LearningResource[] => {
  const resourceDatabase: Record<string, LearningResource[]> = {
    演算法: [
      {
        title: "演算法與資料結構完整教學",
        url: "https://www.youtube.com/watch?v=8hly31xKli0",
        type: "youtube",
        description: "完整的演算法基礎概念教學",
      },
      {
        title: "LeetCode 演算法練習",
        url: "https://leetcode.com/",
        type: "website",
        description: "線上演算法題目練習平台",
      },
    ],
    排序: [
      {
        title: "排序演算法視覺化教學",
        url: "https://www.youtube.com/watch?v=kPRA0W1kECg",
        type: "youtube",
        description: "各種排序演算法的動畫演示",
      },
      {
        title: "排序演算法比較",
        url: "https://visualgo.net/en/sorting",
        type: "website",
        description: "互動式排序演算法視覺化工具",
      },
    ],
    網頁: [
      {
        title: "HTML CSS JavaScript 完整教學",
        url: "https://www.youtube.com/watch?v=UB1O30fR-EE",
        type: "youtube",
        description: "前端開發基礎教學",
      },
      {
        title: "MDN Web 文檔",
        url: "https://developer.mozilla.org/",
        type: "documentation",
        description: "權威的網頁開發技術文檔",
      },
    ],
    程式: [
      {
        title: "程式設計入門教學",
        url: "https://www.youtube.com/watch?v=zOjov-2OZ0E",
        type: "youtube",
        description: "程式設計基礎概念",
      },
      {
        title: "GitHub 程式碼範例",
        url: "https://github.com/",
        type: "website",
        description: "開源程式碼學習平台",
      },
    ],
    資料結構: [
      {
        title: "資料結構詳解",
        url: "https://www.youtube.com/watch?v=RBSGKlAvoiM",
        type: "youtube",
        description: "各種資料結構的實作與應用",
      },
      {
        title: "資料結構視覺化",
        url: "https://www.cs.usfca.edu/~galles/visualization/Algorithms.html",
        type: "website",
        description: "互動式資料結構學習工具",
      },
    ],
    專案: [
      {
        title: "專案開發流程教學",
        url: "https://www.youtube.com/watch?v=7EHnQ0VM4KY",
        type: "youtube",
        description: "軟體專案開發完整流程",
      },
      {
        title: "專案管理工具",
        url: "https://trello.com/",
        type: "website",
        description: "線上專案管理平台",
      },
    ],
    報告: [
      {
        title: "學術報告撰寫技巧",
        url: "https://www.youtube.com/watch?v=WK7khA0Q1DA",
        type: "youtube",
        description: "如何撰寫高品質的學術報告",
      },
      {
        title: "簡報設計工具",
        url: "https://www.canva.com/",
        type: "website",
        description: "專業簡報設計平台",
      },
    ],
  }

  const matchedResources: LearningResource[] = []

  keywords.forEach((keyword) => {
    Object.keys(resourceDatabase).forEach((key) => {
      if (keyword.includes(key) || key.includes(keyword)) {
        matchedResources.push(...resourceDatabase[key])
      }
    })
  })

  // 去重並限制數量
  const uniqueResources = matchedResources.filter(
    (resource, index, self) => index === self.findIndex((r) => r.url === resource.url),
  )

  return uniqueResources.slice(0, 6)
}

const getTypeIcon = (type: LearningResource["type"]) => {
  switch (type) {
    case "youtube":
      return "🎥"
    case "website":
      return "🌐"
    case "documentation":
      return "📚"
    default:
      return "🔗"
  }
}

const getTypeText = (type: LearningResource["type"]) => {
  switch (type) {
    case "youtube":
      return "YouTube"
    case "website":
      return "網站"
    case "documentation":
      return "文檔"
    default:
      return "連結"
  }
}

export function LearningResources({ assignment, course, searchQuery }: LearningResourcesProps) {
  const [customSearch, setCustomSearch] = useState("")
  const [showCustomSearch, setShowCustomSearch] = useState(false)
  const [customResources, setCustomResources] = useState<LearningResource[]>([])
  const [isDragOver, setIsDragOver] = useState(false)

  // 生成搜索關鍵字
  const generateKeywords = (): string[] => {
    const keywords: string[] = []

    if (customSearch.trim()) {
      keywords.push(customSearch.trim())
    } else if (searchQuery) {
      keywords.push(searchQuery)
    } else if (assignment) {
      keywords.push(assignment.title)
      if (assignment.description) {
        keywords.push(assignment.description)
      }
    }

    if (course) {
      keywords.push(course.name)
    }

    return keywords
  }

  const keywords = generateKeywords()
  const resources = getResourcesByKeywords(keywords)
  const allResources = [...resources, ...customResources]

  const handleCustomSearch = () => {
    if (customSearch.trim()) {
      // 觸發重新搜索
      setShowCustomSearch(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.currentTarget === e.target) {
      setIsDragOver(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    let url = e.dataTransfer.getData("text/uri-list")
    if (!url) {
      url = e.dataTransfer.getData("text/plain")
    }
    if (!url) {
      url = e.dataTransfer.getData("URL")
    }

    console.log("[v0] Dropped data:", url)

    if (url && (url.startsWith("http://") || url.startsWith("https://"))) {
      // Check if URL already exists
      const existsInDefault = resources.some((resource) => resource.url === url)
      const existsInCustom = customResources.some((resource) => resource.url === url)

      if (existsInDefault || existsInCustom) {
        console.log("[v0] URL already exists:", url)
        return // Don't add duplicate
      }

      // Extract info based on URL type
      const youtubeInfo = extractYouTubeInfo(url)
      const websiteInfo = extractWebsiteInfo(url)

      const newResource: LearningResource = {
        url,
        ...(youtubeInfo || websiteInfo),
      }

      console.log("[v0] Adding new resource:", newResource)
      setCustomResources((prev) => [newResource, ...prev])
    } else {
      console.log("[v0] Invalid URL or no URL found:", url)
    }
  }

  const removeCustomResource = (urlToRemove: string) => {
    setCustomResources((prev) => prev.filter((resource) => resource.url !== urlToRemove))
  }

  return (
    <Card
      className={`p-4 transition-all duration-200 ${
        isDragOver ? "bg-primary/5 border-primary border-2 border-dashed shadow-lg" : "hover:shadow-md"
      }`}
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-foreground flex items-center gap-2">
          <span>🎯</span>
          學習資源推薦
        </h2>
        <Button variant="outline" size="sm" onClick={() => setShowCustomSearch(!showCustomSearch)}>
          自訂搜索
        </Button>
      </div>

      {showCustomSearch && (
        <div className="mb-4 p-3 bg-muted rounded-lg">
          <div className="flex gap-2">
            <Input
              placeholder="輸入搜索關鍵字..."
              value={customSearch}
              onChange={(e) => setCustomSearch(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleCustomSearch()}
            />
            <Button size="sm" onClick={handleCustomSearch}>
              搜索
            </Button>
          </div>
        </div>
      )}

      {isDragOver && (
        <div className="mb-4 p-4 border-2 border-dashed border-primary bg-primary/5 rounded-lg text-center">
          <p className="text-primary font-medium">📎 放開以新增學習資源</p>
          <p className="text-xs text-muted-foreground mt-1">支援 YouTube 影片和網站連結</p>
        </div>
      )}

      {keywords.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-muted-foreground">搜索關鍵字：{keywords.join(", ")}</p>
        </div>
      )}

      {allResources.length > 0 ? (
        <div className="space-y-3">
          {allResources.map((resource, index) => {
            const isCustomResource = customResources.some((cr) => cr.url === resource.url)

            return (
              <div
                key={index}
                className="flex items-start justify-between p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors"
              >
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-lg">{getTypeIcon(resource.type)}</span>
                    <span className="text-xs px-2 py-1 bg-background rounded-full text-muted-foreground">
                      {getTypeText(resource.type)}
                    </span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-foreground text-balance mb-1">{resource.title}</h3>
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{resource.description}</p>
                  </div>
                </div>

                <div className="flex-shrink-0 ml-3 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(resource.url, "_blank")}
                    className="text-xs"
                  >
                    開啟連結
                  </Button>
                  {isCustomResource && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeCustomResource(resource.url)}
                      className="text-xs text-destructive hover:text-destructive"
                    >
                      刪除
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-6">
          <p className="text-muted-foreground mb-2">找不到相關學習資源</p>
          <p className="text-xs text-muted-foreground">嘗試使用不同的關鍵字搜索或拖曳連結新增資源</p>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-border">
        <p className="text-xs text-muted-foreground text-center">
          💡 提示：點擊「自訂搜索」可以搜索特定主題的學習資源，或直接拖曳網址到此區域新增
        </p>
      </div>
    </Card>
  )
}
