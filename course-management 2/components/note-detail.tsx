"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PageHeader } from "@/components/page-header"
import { PaperclipIcon, DownloadIcon, EyeIcon } from "@/components/icons"
import { useState } from "react"
import { ApiService } from "@/services/apiService"
import type { Note, Course } from "@/types/course"

interface NoteDetailProps {
  note: Note
  course?: Course
  onBack: () => void
  onEdit: () => void
  onDelete: () => void
}

export function NoteDetail({ note, course, onBack, onEdit, onDelete }: NoteDetailProps) {
  const [previewFile, setPreviewFile] = useState<{ name: string; url: string; type: string } | null>(null)

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const handleDownload = (attachment: { name: string; url: string }) => {
    const link = document.createElement("a")
    const absoluteUrl = attachment.url?.startsWith("http")
      ? attachment.url
      : `${ApiService.backendOrigin}${attachment.url}`
    link.href = absoluteUrl
    link.download = attachment.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handlePreview = (attachment: { name: string; url: string; type: string }) => {
    const absoluteUrl = attachment.url?.startsWith("http")
      ? attachment.url
      : `${ApiService.backendOrigin}${attachment.url}`
    setPreviewFile({ ...attachment, url: absoluteUrl })
  }

  const isPreviewable = (type: string, fileName: string) => {
    const extension = fileName.toLowerCase().split(".").pop() || ""

    // Images
    if (type.startsWith("image/") || ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"].includes(extension)) {
      return true
    }

    // PDF
    if (type === "application/pdf" || extension === "pdf") {
      return true
    }

    // Microsoft Office files
    if (
      type === "application/msword" ||
      type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
      type === "application/vnd.ms-excel" ||
      type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
      type === "application/vnd.ms-powerpoint" ||
      type === "application/vnd.openxmlformats-officedocument.presentationml.presentation" ||
      ["doc", "docx", "xls", "xlsx", "ppt", "pptx"].includes(extension)
    ) {
      return true
    }

    // Video files
    if (type.startsWith("video/") || ["mp4", "webm", "ogg", "avi", "mov", "wmv", "flv"].includes(extension)) {
      return true
    }

    // Audio files
    if (type.startsWith("audio/") || ["mp3", "wav", "ogg", "aac", "m4a", "flac"].includes(extension)) {
      return true
    }

    return false
  }

  const renderPreviewContent = () => {
    if (!previewFile) return null

    // Images
    if (previewFile.type.startsWith("image/")) {
      return (
        <img
          src={previewFile.url || "/placeholder.svg"}
          alt={previewFile.name}
          className="max-w-full max-h-[60vh] object-contain rounded-lg"
        />
      )
    }

    // PDF
    if (previewFile.type === "application/pdf") {
      return <embed src={previewFile.url} type="application/pdf" className="w-full h-[60vh] rounded-lg border" />
    }

    // Microsoft Office files (Word/Excel/PPT)
    if (previewFile.type.startsWith("application/vnd.")) {
      return (
        <iframe
          src={`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(previewFile.url)}`}
          className="w-full h-[60vh] rounded-lg border"
          title={previewFile.name}
        ></iframe>
      )
    }

    // Text files
    if (previewFile.type.startsWith("text/")) {
      return (
        <div className="w-full h-[60vh] overflow-auto bg-gray-50 rounded-lg">
          <iframe src={previewFile.url} className="w-full h-full border-0" title={previewFile.name}></iframe>
        </div>
      )
    }

    // Video files
    if (previewFile.type.startsWith("video/")) {
      return (
        <video controls className="max-w-full max-h-[60vh] rounded-lg">
          您的瀏覽器不支援影片播放
        </video>
      )
    }

    // Audio files
    if (previewFile.type.startsWith("audio/")) {
      return (
        <div className="w-full max-w-md">
          <audio controls className="w-full">
            您的瀏覽器不支援音訊播放
          </audio>
        </div>
      )
    }

    // Unsupported file type
    return <p className="text-center py-8 text-muted-foreground">不支援的檔案類型</p>
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
              <PaperclipIcon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">附加檔案 ({note.attachments.length})</span>
            </div>
            <div className="space-y-2">
              {note.attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <PaperclipIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{attachment.name}</p>
                      <p className="text-xs text-muted-foreground">{formatFileSize(attachment.size)}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {isPreviewable(attachment.type, attachment.name) && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handlePreview(attachment)}
                        className="flex-shrink-0"
                        title="預覽檔案"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownload(attachment)}
                      className="flex-shrink-0"
                      title="下載檔案"
                    >
                      <DownloadIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {previewFile && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold truncate">{previewFile.name}</h3>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => handleDownload(previewFile)}>
                  <DownloadIcon className="h-4 w-4 mr-1" />
                  下載
                </Button>
                <Button variant="outline" size="sm" onClick={() => setPreviewFile(null)}>
                  關閉
                </Button>
              </div>
            </div>
            <div className="p-4 flex justify-center">{renderPreviewContent()}</div>
          </div>
        </div>
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
