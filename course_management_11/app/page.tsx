"use client"

import { useState } from "react"
import { BottomNavigation } from "@/components/bottom-navigation"
import { PageHeader } from "@/components/page-header"
import { CourseForm } from "@/components/course-form"
import { CourseCard } from "@/components/course-card"
import { CourseDetail } from "@/components/course-detail"
import { CourseCalendar } from "@/components/course-calendar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ExclamationIcon, PlusIcon, CalendarIcon, ListIcon } from "@/components/icons"
import { useCourses } from "@/hooks/use-courses"
import { AssignmentForm } from "@/components/assignment-form"
import { AssignmentCard } from "@/components/assignment-card"
import { AssignmentFilters } from "@/components/assignment-filters"
import { AssignmentDetail } from "@/components/assignment-detail"
import { NoteForm } from "@/components/note-form"
import { NoteCard } from "@/components/note-card"
import { NoteFilters } from "@/components/note-filters"
import { NoteDetail } from "@/components/note-detail"
import { DashboardStats } from "@/components/dashboard-stats"
import { UpcomingSchedule } from "@/components/upcoming-schedule"
import { RecentNotes } from "@/components/recent-notes"
import { RecentExams } from "@/components/recent-exams"
import { FloatingActionButton } from "@/components/floating-action-button"
import { ExamForm } from "@/components/exam-form"
import { ExamDetail } from "@/components/exam-detail"
import { ExamCard } from "@/components/exam-card"
import { ExamFilters } from "@/components/exam-filters"
import { ScrollSummary } from "@/components/scroll-summary"
import { TaskTypeToggle } from "@/components/task-type-toggle"
import { getTaiwanTime, getDaysDifferenceTaiwan, isTodayTaiwan, isSameDayTaiwan } from "@/lib/taiwan-time"

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("home")
  const [showCourseForm, setShowCourseForm] = useState(false)
  const [editingCourse, setEditingCourse] = useState<string | null>(null)
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null)
  const [showAssignmentForm, setShowAssignmentForm] = useState(false)
  const [editingAssignment, setEditingAssignment] = useState<string | null>(null)
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<string | null>(null)
  const [assignmentFilter, setAssignmentFilter] = useState("all")
  const [showNoteForm, setShowNoteForm] = useState(false)
  const [editingNote, setEditingNote] = useState<string | null>(null)
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null)
  const [noteFilter, setNoteFilter] = useState("all")
  const [noteSortBy, setNoteSortBy] = useState("updatedAt")
  const [noteSearchQuery, setNoteSearchQuery] = useState("")
  const [showExamForm, setShowExamForm] = useState(false)
  const [editingExam, setEditingExam] = useState<string | null>(null)
  const [selectedExamId, setSelectedExamId] = useState<string | null>(null)
  const [examFilter, setExamFilter] = useState("all")
  const [courseView, setCourseView] = useState<"list" | "calendar">("list")
  const [taskType, setTaskType] = useState<"assignment" | "exam">("assignment")
  const [selectedDate, setSelectedDate] = useState(new Date())

  const {
    courses,
    assignments,
    notes,
    exams,
    addCourse,
    updateCourse,
    getCourseById,
    getAssignmentsByCourse,
    getNotesByCourse,
    getExamsByCourse,
    addAssignment,
    updateAssignment,
    deleteAssignment,
    getAssignmentById,
    addNote,
    updateNote,
    deleteNote,
    addExam,
    updateExam,
    deleteExam,
    getExamById,
    deleteCourse,
  } = useCourses()

  const getNoteById = (id: string) => {
    return notes.find((note) => note.id === id)
  }

  const renderContent = () => {
    if (showExamForm) {
      return (
        <div>
          <PageHeader title={editingExam ? "編輯考試" : "新增考試"} />
          <ExamForm
            courses={courses}
            initialData={editingExam ? getExamById(editingExam) : undefined}
            onSubmit={(examData) => {
              if (editingExam) {
                updateExam(editingExam, examData)
              } else {
                addExam(examData)
              }
              setShowExamForm(false)
              setEditingExam(null)
            }}
            onCancel={() => {
              setShowExamForm(false)
              setEditingExam(null)
            }}
          />
        </div>
      )
    }

    if (activeTab === "courses") {
      if (selectedCourseId) {
        const course = getCourseById(selectedCourseId)
        if (course) {
          return (
            <CourseDetail
              course={course}
              assignments={getAssignmentsByCourse(selectedCourseId)}
              notes={getNotesByCourse(selectedCourseId)}
              exams={getExamsByCourse(selectedCourseId)}
              onBack={() => setSelectedCourseId(null)}
              onViewAssignment={(assignment) => {
                setSelectedAssignmentId(assignment.id)
                setTaskType("assignment")
                setActiveTab("tasks")
              }}
              onViewExam={(exam) => {
                setSelectedExamId(exam.id)
                setTaskType("exam")
                setActiveTab("tasks")
              }}
              onViewNote={(note) => {
                setSelectedNoteId(note.id)
                setActiveTab("notes")
              }}
              onEdit={() => {
                setEditingCourse(selectedCourseId)
                setSelectedCourseId(null)
                setShowCourseForm(true)
              }}
              onDelete={() => {
                deleteCourse(selectedCourseId)
                setSelectedCourseId(null)
              }}
            />
          )
        }
      }

      if (showCourseForm) {
        return (
          <div>
            <PageHeader title={editingCourse ? "編輯課程" : "新增課程"} />
            <CourseForm
              initialCourse={editingCourse ? getCourseById(editingCourse) : undefined}
              onSubmit={(courseData) => {
                if (editingCourse) {
                  updateCourse(editingCourse, courseData)
                } else {
                  addCourse(courseData)
                }
                setShowCourseForm(false)
                setEditingCourse(null)
              }}
              onCancel={() => {
                setShowCourseForm(false)
                setEditingCourse(null)
              }}
            />
          </div>
        )
      }

      return <CoursesContent />
    }

    if (activeTab === "tasks") {
      if (selectedAssignmentId) {
        const assignment = getAssignmentById(selectedAssignmentId)
        if (assignment) {
          return (
            <AssignmentDetail
              assignment={assignment}
              course={getCourseById(assignment.courseId)}
              onBack={() => setSelectedAssignmentId(null)}
              onEdit={() => {
                setEditingAssignment(assignment.id)
                setSelectedAssignmentId(null)
                setShowAssignmentForm(true)
              }}
              onDelete={() => {
                if (confirm("確定要刪除這個作業嗎？")) {
                  deleteAssignment(assignment.id)
                  setSelectedAssignmentId(null)
                }
              }}
              onStatusChange={(status) => {
                updateAssignment(selectedAssignmentId, { status })
              }}
            />
          )
        }
      }

      if (selectedExamId) {
        const exam = getExamById(selectedExamId)
        if (exam) {
          return (
            <ExamDetail
              exam={exam}
              course={getCourseById(exam.courseId)}
              onBack={() => setSelectedExamId(null)}
              onEdit={() => {
                setEditingExam(exam.id)
                setSelectedExamId(null)
                setShowExamForm(true)
              }}
              onDelete={() => {
                if (confirm("確定要刪除這個考試嗎？")) {
                  deleteExam(exam.id)
                  setSelectedExamId(null)
                }
              }}
              onStatusChange={(id, status) => updateExam(id, { status })}
            />
          )
        }
      }

      if (showAssignmentForm) {
        return (
          <div>
            <PageHeader title={editingAssignment ? "編輯作業" : "新增作業"} />
            <AssignmentForm
              courses={courses}
              initialData={editingAssignment ? getAssignmentById(editingAssignment) : undefined}
              onSubmit={(assignmentData) => {
                if (editingAssignment) {
                  updateAssignment(editingAssignment, assignmentData)
                } else {
                  addAssignment(assignmentData)
                }
                setShowAssignmentForm(false)
                setEditingAssignment(null)
              }}
              onCancel={() => {
                setShowAssignmentForm(false)
                setEditingAssignment(null)
              }}
            />
          </div>
        )
      }

      if (showExamForm) {
        return (
          <div>
            <PageHeader title={editingExam ? "編輯考試" : "新增考試"} />
            <ExamForm
              courses={courses}
              initialData={editingExam ? getExamById(editingExam) : undefined}
              onSubmit={(examData) => {
                if (editingExam) {
                  updateExam(editingExam, examData)
                } else {
                  addExam(examData)
                }
                setShowExamForm(false)
                setEditingExam(null)
              }}
              onCancel={() => {
                setShowExamForm(false)
                setEditingExam(null)
              }}
            />
          </div>
        )
      }

      return <TasksContent />
    }

    if (activeTab === "notes") {
      if (selectedNoteId) {
        const note = getNoteById(selectedNoteId)
        if (note) {
          return (
            <NoteDetail
              note={note}
              course={getCourseById(note.courseId)}
              onBack={() => setSelectedNoteId(null)}
              onEdit={() => {
                setEditingNote(note.id)
                setSelectedNoteId(null)
                setShowNoteForm(true)
              }}
              onDelete={() => {
                if (confirm("確定要刪除這個筆記嗎？")) {
                  deleteNote(note.id)
                  setSelectedNoteId(null)
                }
              }}
            />
          )
        }
      }

      if (showNoteForm) {
        return (
          <div>
            <PageHeader title={editingNote ? "編輯筆記" : "新增筆記"} />
            <NoteForm
              courses={courses}
              initialData={editingNote ? getNoteById(editingNote) : undefined}
              onSubmit={(noteData) => {
                if (editingNote) {
                  updateNote(editingNote, noteData)
                } else {
                  addNote(noteData)
                }
                setShowNoteForm(false)
                setEditingNote(null)
              }}
              onCancel={() => {
                setShowNoteForm(false)
                setEditingNote(null)
              }}
            />
          </div>
        )
      }

      return <NotesContent />
    }

    switch (activeTab) {
      case "home":
        return <HomeContent />
      default:
        return <HomeContent />
    }
  }

  function HomeContent() {
    const taiwanNow = getTaiwanTime()
    const selectedDay = selectedDate.getDay()
    const isViewingToday = isTodayTaiwan(selectedDate)

    const dateCourses = courses.filter((course) => course.schedule.some((slot) => slot.dayOfWeek === selectedDay))

    const urgentAssignments = assignments
      .filter((assignment) => {
        if (assignment.status === "completed") return false

        if (assignment.notificationTime) {
          return taiwanNow >= assignment.notificationTime
        }

        const daysUntilDue = getDaysDifferenceTaiwan(selectedDate, assignment.dueDate)
        return daysUntilDue <= 7 && daysUntilDue >= 0
      })
      .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())

    return (
      <>
        <ScrollSummary
          courses={courses}
          assignments={assignments}
          exams={exams}
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
        />

        <DashboardStats courses={courses} assignments={assignments} notes={notes} exams={exams} />

        <UpcomingSchedule courses={courses} selectedDate={selectedDate} />

        <Card className="bg-white p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-foreground flex items-center gap-2">
              <ExclamationIcon className="w-5 h-5 text-destructive" />
              緊急作業
            </h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setActiveTab("tasks")
                setTaskType("assignment")
                setAssignmentFilter("pending")
              }}
            >
              查看全部
            </Button>
          </div>

          {urgentAssignments.length > 0 ? (
            <div className="space-y-3">
              {urgentAssignments.slice(0, 3).map((assignment) => {
                const course = getCourseById(assignment.courseId)
                const daysUntilDue = getDaysDifferenceTaiwan(selectedDate, assignment.dueDate)
                const isUrgent = daysUntilDue <= 1

                return (
                  <div
                    key={assignment.id}
                    className="flex items-center justify-between p-2 bg-muted rounded-lg cursor-pointer hover:shadow-sm transition-shadow"
                    onClick={() => {
                      setSelectedAssignmentId(assignment.id)
                      setTaskType("assignment")
                      setActiveTab("tasks")
                    }}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-1 h-8 flex-shrink-0 rounded-sm"
                        style={{ backgroundColor: isUrgent ? "#ef4444" : "#f59e0b" }}
                      />
                      <div>
                        <p className="text-sm font-medium text-foreground">{assignment.title}</p>
                        <p className="text-xs text-muted-foreground">{course?.name}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-xs font-medium ${isUrgent ? "text-destructive" : "text-chart-5"}`}>
                        {isSameDayTaiwan(assignment.dueDate, selectedDate)
                          ? isViewingToday
                            ? "今天到期"
                            : "當天到期"
                          : daysUntilDue === 1
                            ? isViewingToday
                              ? "明天到期"
                              : "隔天到期"
                            : `${daysUntilDue}天後到期`}
                      </p>
                      <p className="text-xs text-muted-foreground">{assignment.dueDate.toLocaleDateString("zh-TW")}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-4">暫無緊急的作業</p>
          )}
        </Card>

        <RecentExams
          exams={exams}
          courses={courses}
          selectedDate={selectedDate}
          onViewExam={(examId) => {
            setSelectedExamId(examId)
            setTaskType("exam")
            setActiveTab("tasks")
          }}
          onViewAllExams={() => {
            setTaskType("exam")
            setActiveTab("tasks")
          }}
        />

        <RecentNotes
          notes={notes}
          courses={courses}
          selectedDate={selectedDate}
          onViewNote={(noteId) => {
            setSelectedNoteId(noteId)
            setActiveTab("notes")
          }}
          onViewAllNotes={() => setActiveTab("notes")}
        />
      </>
    )
  }

  function CoursesContent() {
    return (
      <>
        <PageHeader
          title="課程管理"
          subtitle="管理你的所有課程"
          action={
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCourseView(courseView === "list" ? "calendar" : "list")}
              >
                {courseView === "list" ? (
                  <CalendarIcon className="w-4 h-4 mr-1" />
                ) : (
                  <ListIcon className="w-4 h-4 mr-1" />
                )}
                {courseView === "list" ? "月曆視圖" : "列表視圖"}
              </Button>
              <Button size="sm" onClick={() => setShowCourseForm(true)}>
                <PlusIcon className="w-4 h-4 mr-1" />
                新增
              </Button>
            </div>
          }
        />

        {courses.length > 0 ? (
          courseView === "list" ? (
            <div className="space-y-3">
              {courses.map((course) => (
                <CourseCard key={course.id} course={course} onClick={() => setSelectedCourseId(course.id)} />
              ))}
            </div>
          ) : (
            <CourseCalendar courses={courses} onCourseClick={(courseId) => setSelectedCourseId(courseId)} />
          )
        ) : (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground mb-4">還沒有任何課程</p>
            <Button onClick={() => setShowCourseForm(true)}>
              <PlusIcon className="w-4 h-4 mr-2" />
              新增第一個課程
            </Button>
          </Card>
        )}
      </>
    )
  }

  function TasksContent() {
    return (
      <>
        <PageHeader
          title="任務管理"
          subtitle="追蹤你的作業與考試"
          action={
            <Button
              size="sm"
              onClick={() => {
                if (taskType === "assignment") {
                  setShowAssignmentForm(true)
                } else {
                  setShowExamForm(true)
                }
              }}
            >
              <PlusIcon className="w-4 h-4 mr-1" />
              新增
            </Button>
          }
        />

        <TaskTypeToggle
          activeType={taskType}
          onTypeChange={setTaskType}
          assignmentCount={assignments.length}
          examCount={exams.length}
        />

        {taskType === "assignment" ? <AssignmentsContent /> : <ExamsContent />}
      </>
    )
  }

  function AssignmentsContent() {
    const updatedAssignments = assignments.map((assignment) => {
      const daysUntilDue = getDaysDifferenceTaiwan(new Date(), assignment.dueDate)
      if (assignment.status === "pending" && daysUntilDue < 0) {
        return { ...assignment, status: "overdue" as const }
      }
      return assignment
    })

    const filteredAssignments = updatedAssignments.filter((assignment) => {
      switch (assignmentFilter) {
        case "pending":
          return assignment.status === "pending"
        case "completed":
          return assignment.status === "completed"
        case "overdue":
          return assignment.status === "overdue"
        default:
          return true
      }
    })

    const sortedAssignments = filteredAssignments.sort((a, b) => {
      if (a.status === "overdue" && b.status !== "overdue") return -1
      if (b.status === "overdue" && a.status !== "overdue") return 1
      return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
    })

    const counts = {
      all: updatedAssignments.length,
      pending: updatedAssignments.filter((a) => a.status === "pending").length,
      completed: updatedAssignments.filter((a) => a.status === "completed").length,
      overdue: updatedAssignments.filter((a) => a.status === "overdue").length,
    }

    return (
      <>
        <AssignmentFilters activeFilter={assignmentFilter} onFilterChange={setAssignmentFilter} counts={counts} />

        {sortedAssignments.length > 0 ? (
          <div className="space-y-4">
            {sortedAssignments.map((assignment) => (
              <AssignmentCard
                key={assignment.id}
                assignment={assignment}
                course={getCourseById(assignment.courseId)}
                onStatusChange={(id, status) => updateAssignment(id, { status })}
                onViewDetail={() => setSelectedAssignmentId(assignment.id)}
                onEdit={() => {
                  setEditingAssignment(assignment.id)
                  setSelectedAssignmentId(null)
                  setShowAssignmentForm(true)
                }}
                onDelete={() => {
                  if (confirm("確定要刪除這個作業嗎？")) {
                    deleteAssignment(assignment.id)
                  }
                }}
              />
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground mb-4">
              {assignmentFilter === "all"
                ? "還沒有任何作業"
                : `沒有${assignmentFilter === "pending" ? "進行中" : assignmentFilter === "completed" ? "已完成" : "已逾期"}的作業`}
            </p>
            {assignmentFilter === "all" && (
              <Button onClick={() => setShowAssignmentForm(true)}>
                <PlusIcon className="w-4 h-4 mr-2" />
                新增第一個作業
              </Button>
            )}
          </Card>
        )}
      </>
    )
  }

  function NotesContent() {
    const filteredNotes = notes.filter((note) => {
      const matchesFilter = noteFilter === "all" || note.courseId === noteFilter
      const matchesSearch =
        noteSearchQuery === "" ||
        note.title.toLowerCase().includes(noteSearchQuery.toLowerCase()) ||
        note.content.toLowerCase().includes(noteSearchQuery.toLowerCase())

      return matchesFilter && matchesSearch
    })

    const sortedNotes = filteredNotes.sort((a, b) => {
      switch (noteSortBy) {
        case "title":
          return a.title.localeCompare(b.title, "zh-TW")
        case "createdAt":
          return b.createdAt.getTime() - a.createdAt.getTime()
        case "updatedAt":
        default:
          return b.updatedAt.getTime() - a.updatedAt.getTime()
      }
    })

    const counts = {
      all: notes.length,
      ...courses.reduce(
        (acc, course) => {
          acc[course.id] = notes.filter((note) => note.courseId === course.id).length
          return acc
        },
        {} as Record<string, number>,
      ),
    }

    return (
      <>
        <PageHeader
          title="筆記管理"
          subtitle="記錄你的學習筆記"
          action={
            <Button size="sm" onClick={() => setShowNoteForm(true)}>
              <PlusIcon className="w-4 h-4 mr-1" />
              新增
            </Button>
          }
        />

        {courses.length > 0 && (
          <NoteFilters
            courses={courses}
            activeFilter={noteFilter}
            onFilterChange={setNoteFilter}
            counts={counts}
            sortBy={noteSortBy}
            onSortChange={setNoteSortBy}
            searchQuery={noteSearchQuery}
            onSearchChange={setNoteSearchQuery}
          />
        )}

        {sortedNotes.length > 0 ? (
          <div className="space-y-4">
            {sortedNotes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                course={getCourseById(note.courseId)}
                onClick={() => setSelectedNoteId(note.id)}
                onEdit={() => {
                  setEditingNote(note.id)
                  setSelectedNoteId(null)
                  setShowNoteForm(true)
                }}
                onDelete={() => {
                  if (confirm("確定要刪除這個筆記嗎？")) {
                    deleteNote(note.id)
                  }
                }}
              />
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground mb-4">
              {noteSearchQuery
                ? "沒有找到符合搜尋條件的筆記"
                : noteFilter === "all"
                  ? "還沒有任何筆記"
                  : "這個課程還沒有筆記"}
            </p>
            {courses.length > 0 && !noteSearchQuery ? (
              <Button onClick={() => setShowNoteForm(true)}>
                <PlusIcon className="w-4 h-4 mr-2" />
                新增第一個筆記
              </Button>
            ) : !courses.length ? (
              <div>
                <p className="text-sm text-muted-foreground mb-2">請先新增課程才能建立筆記</p>
                <Button
                  onClick={() => {
                    setActiveTab("courses")
                    setShowCourseForm(true)
                  }}
                >
                  新增課程
                </Button>
              </div>
            ) : null}
          </Card>
        )}
      </>
    )
  }

  function ExamsContent() {
    const now = new Date()
    const oneWeekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

    const filteredExams = exams.filter((exam) => {
      const examDate = new Date(exam.examDate)

      switch (examFilter) {
        case "upcoming":
          return examDate >= now && examDate <= oneWeekFromNow && exam.status !== "completed"
        case "scheduled":
          return examDate > oneWeekFromNow && exam.status !== "completed"
        case "completed":
          return exam.status === "completed" || examDate < now
        default:
          return true
      }
    })

    const sortedExams = filteredExams.sort((a, b) => {
      return new Date(a.examDate).getTime() - new Date(b.examDate).getTime()
    })

    const counts = {
      all: exams.length,
      upcoming: exams.filter((e) => {
        const examDate = new Date(e.examDate)
        return examDate >= now && examDate <= oneWeekFromNow && e.status !== "completed"
      }).length,
      scheduled: exams.filter((e) => {
        const examDate = new Date(e.examDate)
        return examDate > oneWeekFromNow && e.status !== "completed"
      }).length,
      completed: exams.filter((e) => {
        const examDate = new Date(e.examDate)
        return e.status === "completed" || examDate < now
      }).length,
    }

    return (
      <>
        <ExamFilters activeFilter={examFilter} onFilterChange={setExamFilter} counts={counts} />

        {sortedExams.length > 0 ? (
          <div className="space-y-4">
            {sortedExams.map((exam) => (
              <ExamCard
                key={exam.id}
                exam={exam}
                course={getCourseById(exam.courseId)}
                onViewDetail={() => setSelectedExamId(exam.id)}
                onEdit={() => {
                  setEditingExam(exam.id)
                  setSelectedExamId(null)
                  setShowExamForm(true)
                }}
                onDelete={() => {
                  if (confirm("確定要刪除這個考試嗎？")) {
                    deleteExam(exam.id)
                  }
                }}
                onStatusChange={(id, status) => updateExam(id, { status })}
              />
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground mb-4">
              {examFilter === "all"
                ? "還沒有任何考試"
                : examFilter === "upcoming"
                  ? "沒有即將來臨的考試"
                  : examFilter === "scheduled"
                    ? "沒有已排程的考試"
                    : "沒有已結束的考試"}
            </p>
            {examFilter === "all" && (
              <Button onClick={() => setShowExamForm(true)}>
                <PlusIcon className="w-4 h-4 mr-2" />
                新增第一個考試
              </Button>
            )}
          </Card>
        )}
      </>
    )
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="container mx-auto px-4 py-6 max-w-md">{renderContent()}</div>
      <BottomNavigation
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab)
          if (tab === "home") {
            setSelectedDate(new Date())
          }
        }}
      />
      <FloatingActionButton
        onAddCourse={() => {
          setActiveTab("courses")
          setShowCourseForm(true)
        }}
        onAddAssignment={() => {
          setActiveTab("tasks")
          setTaskType("assignment")
          setShowAssignmentForm(true)
        }}
        onAddNote={() => {
          setActiveTab("notes")
          setShowNoteForm(true)
        }}
        onAddExam={() => {
          setActiveTab("tasks")
          setTaskType("exam")
          setShowExamForm(true)
        }}
      />
    </div>
  )
}
