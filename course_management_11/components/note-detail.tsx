"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PageHeader } from "@/components/page-header"
import { PaperClipIcon, ArrowDownTrayIcon } from "@heroicons/react/24/outline"
import type { Note, Course } from "@/types/course"

interface NoteDetailProps {
  note: Note
  course?: Course
  onBack: () => void
  onEdit: () => void
  onDelete: () => void
}

export function NoteDetail({ note, course, onBack, onEdit, onDelete }: NoteDetailProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const handleDownload = (attachment: { name: string; url: string }) => {
    const link = document.createElement("a")
    link.href = attachment.url
    link.download = attachment.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <>
      <PageHeader
        title={note.title}
        action={
          <Button variant="outline" size="sm" onClick={onBack}>
            返回
          </Button>
        }
      />

      <div className="space-y-6 mb-6">
        {/* Course Info */}
        <div className="space-y-3">
          {course && (
            <span className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
              {course.name}
            </span>
          )}
        </div>

        {/* Timestamps */}
        <div className="space-y-2">
          <div className="space-y-1">
            <span className="text-sm font-medium">建立時間</span>
            <p className="text-sm text-muted-foreground">{note.createdAt.toLocaleString("zh-TW")}</p>
          </div>

          {note.updatedAt.getTime() !== note.createdAt.getTime() && (
            <div className="space-y-1">
              <span className="text-sm font-medium">最後更新</span>
              <p className="text-sm text-muted-foreground">{note.updatedAt.toLocaleString("zh-TW")}</p>
            </div>
          )}
        </div>
      </div>

      {/* Note Content */}
      <Card className="p-4 mb-4">
        <div className="prose prose-sm max-w-none">
          <div
            className="text-foreground leading-relaxed [&>*]:mb-2 [&>ul]:list-disc [&>ul]:ml-6 [&>ol]:list-decimal [&>ol]:ml-6 [&>a]:text-blue-600 [&>a]:underline [&>strong]:font-bold [&>em]:italic"
            dangerouslySetInnerHTML={{ __html: note.content }}
          />
        </div>
      </Card>

      {note.attachments && note.attachments.length > 0 && (
        <Card className="p-4 mb-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <PaperClipIcon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">附加檔案 ({note.attachments.length})</span>
            </div>
            <div className="space-y-2">
              {note.attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <PaperClipIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{attachment.name}</p>
                      <p className="text-xs text-muted-foreground">{formatFileSize(attachment.size)}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDownload(attachment)}
                    className="flex-shrink-0"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <Button onClick={onEdit} className="flex-1">
          編輯筆記
        </Button>
        <Button
          variant="outline"
          onClick={onDelete}
          className="flex-1 text-destructive hover:text-destructive bg-transparent"
        >
          刪除筆記
        </Button>
      </div>
    </>
  )
}
