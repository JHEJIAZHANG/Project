"use client"

import { CourseDetail } from "@/components/course-detail"
import { useRouter } from "next/navigation"

interface CoursePageProps {
  params: {
    id: string
  }
}

export default function CoursePage({ params }: CoursePageProps) {
  const router = useRouter()

  const handleViewAssignment = (assignmentId: string) => {
    router.push(`/?tab=tasks&assignment=${assignmentId}`)
  }

  const handleViewExam = (examId: string) => {
    router.push(`/?tab=tasks&exam=${examId}`)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6 pb-20 lg:pb-6">
        <CourseDetail
          courseId={params.id}
          showBackButton={true}
          onViewAssignment={handleViewAssignment}
          onViewExam={handleViewExam}
        />
      </div>
    </div>
  )
}
