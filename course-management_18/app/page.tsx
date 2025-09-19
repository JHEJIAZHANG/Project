"use client"

import { useState, useEffect } from "react"
import { BottomNavigation } from "@/components/bottom-navigation"
import { SidebarNavigation } from "@/components/sidebar-navigation"
import { PageHeader } from "@/components/page-header"
import { CourseForm } from "@/components/course-form"
import { CourseCard } from "@/components/course-card"
import { CourseCalendar } from "@/components/course-calendar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PlusIcon, CalendarIcon, ListIcon } from "@/components/icons"
import { useCourses } from "@/hooks/use-courses"
import { AssignmentForm } from "@/components/assignment-form"
import { AssignmentCard } from "@/components/assignment-card"
import { AssignmentFilters } from "@/components/assignment-filters"
import { AssignmentDetail } from "@/components/assignment-detail"
import { NoteForm } from "@/components/note-form"
import { NoteCard } from "@/components/note-card"
import { NoteFilters } from "@/components/note-filters"
import { NoteDetail } from "@/components/note-detail"
import { UpcomingSchedule } from "@/components/upcoming-schedule"
import { FloatingActionButton } from "@/components/floating-action-button"
import { ExamForm } from "@/components/exam-form"
import { ExamDetail } from "@/components/exam-detail"
import { ExamCard } from "@/components/exam-card"
import { ExamFilters } from "@/components/exam-filters"
import { ScrollSummary } from "@/components/scroll-summary"
import { TaskTypeToggle } from "@/components/task-type-toggle"
import { ProfileContent } from "@/components/profile-content"
import { CompactMonthlyCalendar } from "@/components/compact-monthly-calendar"
import { AddCourseDropdown } from "@/components/add-course-dropdown"
import { GoogleClassroomImport } from "@/components/google-classroom-import"
import { getTaiwanTime, isTodayTaiwan, isExamEndedTaiwan, getDaysDifferenceTaiwan } from "@/lib/taiwan-time"
import type { Course } from "@/types/course"
import { CustomCategoryForm, type CustomCategoryItem } from "@/components/custom-category-form"
import { UnifiedTodoSection } from "@/components/unified-todo-section"
import { CustomCategoryFilters } from "@/components/custom-category-filters"
import { CustomCategoryDetail } from "@/components/custom-category-detail"
import { CustomCategoryCard } from "@/components/custom-category-card" // Added import for CustomCategoryCard
import { getNotificationSettings } from "@/components/profile-content"
import { GoogleClassroomSync } from "@/components/google-classroom-sync"

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
  const [taskType, setTaskType] = useState<string>("assignment") // Changed to string to support custom categories
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showGoogleClassroomImport, setShowGoogleClassroomImport] = useState(false)
  const [customCategories, setCustomCategories] = useState<string[]>([]) // Added state for custom categories
  const [customCategoryItems, setCustomCategoryItems] = useState<CustomCategoryItem[]>([])
  const [showCustomCategoryForm, setShowCustomCategoryForm] = useState(false)
  const [editingCustomCategory, setEditingCustomCategory] = useState<string | null>(null)
  const [selectedCustomCategoryId, setSelectedCustomCategoryId] = useState<string | null>(null)
  const [customCategoryFilter, setCustomCategoryFilter] = useState("all") // Added custom category filter state
  const [notificationSettings, setNotificationSettings] = useState(() => getNotificationSettings())

  const [user, setUser] = useState<{
    id: string
    name: string
    email: string
    avatar?: string
    isLoggedIn: boolean
  }>({
    id: "1",
    name: "學生",
    email: "student@example.com",
    avatar: "",
    isLoggedIn: false,
  })

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

  const getCustomCategoryItemById = (id: string) => {
    return customCategoryItems.find((item) => item.id === id)
  }

  useEffect(() => {
    const stored = localStorage.getItem("customCategoryItems")
    if (stored) {
      try {
        const parsedItems = JSON.parse(stored)
        // Convert date strings back to Date objects
        const itemsWithDates = parsedItems.map((item: any) => ({
          ...item,
          dueDate: new Date(item.dueDate),
          createdAt: new Date(item.createdAt),
          updatedAt: new Date(item.updatedAt),
        }))
        setCustomCategoryItems(itemsWithDates)
        console.log("[v0] Loaded custom category items from localStorage:", itemsWithDates.length)
      } catch (error) {
        console.error("[v0] Failed to parse custom category items from localStorage:", error)
      }
    }
  }, [])

  useEffect(() => {
    if (customCategoryItems.length > 0) {
      localStorage.setItem("customCategoryItems", JSON.stringify(customCategoryItems))
      console.log("[v0] Saved custom category items to localStorage:", customCategoryItems.length)
    }
  }, [customCategoryItems])

  useEffect(() => {
    const stored = localStorage.getItem("customCategories")
    if (stored) {
      try {
        const parsedCategories = JSON.parse(stored)
        setCustomCategories(parsedCategories)
        console.log("[v0] Loaded custom categories from localStorage:", parsedCategories)
      } catch (error) {
        console.error("[v0] Failed to parse custom categories from localStorage:", error)
      }
    }
  }, [])

  useEffect(() => {
    if (customCategories.length > 0) {
      localStorage.setItem("customCategories", JSON.stringify(customCategories))
      console.log("[v0] Saved custom categories to localStorage:", customCategories)
    }
  }, [customCategories])

  const addCustomCategoryItem = (itemData: Omit<CustomCategoryItem, "id" | "createdAt" | "updatedAt">) => {
    const newItem: CustomCategoryItem = {
      ...itemData,
      id: Date.now().toString(),
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    console.log("[v0] Adding new custom category item:", newItem)
    setCustomCategoryItems((prev) => [...prev, newItem])
  }

  const updateCustomCategoryItem = (id: string, updates: Partial<CustomCategoryItem>) => {
    console.log("[v0] Updating custom category item:", id, updates)
    setCustomCategoryItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...updates, updatedAt: new Date() } : item)),
    )
  }

  const deleteCustomCategoryItem = (id: string) => {
    console.log("[v0] Deleting custom category item:", id)
    setCustomCategoryItems((prev) => prev.filter((item) => item.id !== id))
  }

  const handleDeleteCategory = (categoryName: string) => {
    if (confirm(`確定要刪除「${categoryName}」分類嗎？這將會刪除該分類下的所有待辦事項。`)) {
      // Remove all items in this category
      setCustomCategoryItems((prev) => prev.filter((item) => item.category !== categoryName))
      // Remove the category itself
      setCustomCategories((prev) => prev.filter((cat) => cat !== categoryName))
      // If currently viewing this category, switch to assignments
      if (taskType === categoryName) {
        setTaskType("assignment")
      }
    }
  }

  const renderContent = () => {
    if (showExamForm) {
      return (
        <div className="pb-20 lg:pb-0">
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

    if (activeTab === "assignments") {
      return (
        <div className="space-y-6">
          <GoogleClassroomSync
            onSync={() => {
              // Refresh assignments after sync
              console.log("[v0] Google Classroom sync completed")
            }}
          />
        </div>
      )
    }

    if (activeTab === "courses") {
      if (showCourseForm) {
        return (
          <div className="pb-20 lg:pb-0">
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

      if (selectedCustomCategoryId) {
        const item = getCustomCategoryItemById(selectedCustomCategoryId)
        if (item) {
          return (
            <div className="pb-20 lg:pb-0">
              <CustomCategoryDetail
                item={item}
                course={getCourseById(item.courseId)}
                onBack={() => setSelectedCustomCategoryId(null)}
                onEdit={() => {
                  setEditingCustomCategory(item.id)
                  setSelectedCustomCategoryId(null)
                  setShowCustomCategoryForm(true)
                }}
                onDelete={() => {
                  if (confirm(`確定要刪除這個${taskType}嗎？`)) {
                    deleteCustomCategoryItem(item.id)
                    setSelectedCustomCategoryId(null)
                  }
                }}
                onStatusChange={(id, status) => updateCustomCategoryItem(id, { status })}
              />
            </div>
          )
        }
      }

      if (showAssignmentForm) {
        return (
          <div className="pb-20 lg:pb-0">
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
          <div className="pb-20 lg:pb-0">
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

      if (showCustomCategoryForm) {
        return (
          <div className="pb-20 lg:pb-0">
            <PageHeader title={editingCustomCategory ? `編輯${taskType || "分類"}` : `新增${taskType || "分類"}`} />
            <CustomCategoryForm
              courses={courses}
              category={taskType}
              initialData={editingCustomCategory ? getCustomCategoryItemById(editingCustomCategory) : undefined}
              onSubmit={(itemData) => {
                if (editingCustomCategory) {
                  updateCustomCategoryItem(editingCustomCategory, itemData)
                } else {
                  addCustomCategoryItem(itemData)
                }
                setShowCustomCategoryForm(false)
                setEditingCustomCategory(null)
              }}
              onCancel={() => {
                setShowCustomCategoryForm(false)
                setEditingCustomCategory(null)
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
          <div className="pb-20 lg:pb-0">
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

    if (activeTab === "profile") {
      return <ProfileContent user={user} onUserChange={setUser} />
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

    return (
      <>
        <div className="space-y-6 lg:grid lg:grid-cols-5 lg:gap-6 lg:space-y-0 mb-6 pb-20 lg:pb-0">
          {/* Mobile: Date (ScrollSummary) - First on mobile */}
          <div className="lg:col-span-2 lg:space-y-6">
            {/* 摘要 */}
            <ScrollSummary
              courses={courses}
              assignments={assignments}
              exams={exams}
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
              user={user}
            />

            {/* Mobile: Recent Courses - Second on mobile, Desktop: stays in left column */}
            <div className="lg:block">
              <UpcomingSchedule courses={courses} selectedDate={selectedDate} />
            </div>

            {/* Mobile: Todo Items - Third on mobile, Desktop: stays in left column */}
            <div className="lg:block">
              <UnifiedTodoSection
                assignments={assignments}
                exams={exams}
                customCategoryItems={customCategoryItems}
                courses={courses}
                selectedDate={selectedDate}
                notificationSettings={{
                  assignmentReminderTiming: notificationSettings.assignmentReminderTiming,
                }}
                onViewItem={(id, type) => {
                  if (type === "assignment") {
                    setSelectedAssignmentId(id)
                    setTaskType("assignment")
                  } else if (type === "exam") {
                    setSelectedExamId(id)
                    setTaskType("exam")
                  } else if (type === "custom") {
                    const item = getCustomCategoryItemById(id)
                    if (item) {
                      setSelectedCustomCategoryId(id)
                      setTaskType(item.category)
                    }
                  }
                  setActiveTab("tasks")
                }}
                onViewAllTodos={() => {
                  setActiveTab("tasks")
                }}
              />
            </div>
          </div>

          {/* Mobile: Calendar - Fourth on mobile, Desktop: right column */}
          <div className="lg:col-span-3">
            <CompactMonthlyCalendar selectedDate={selectedDate} onDateSelect={setSelectedDate} />
          </div>
        </div>
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
                {courseView === "list" ? "週視圖" : "列表視圖"}
              </Button>
              <AddCourseDropdown
                onManualAdd={() => setShowCourseForm(true)}
                onGoogleClassroomImport={() => setShowGoogleClassroomImport(true)}
              />
            </div>
          }
        />

        {courses.length > 0 ? (
          courseView === "list" ? (
            <div className="space-y-3 pb-20 lg:pb-0">
              {courses.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
          ) : (
            <div className="pb-20 lg:pb-0">
              <CourseCalendar courses={courses} onCourseClick={(courseId) => setSelectedCourseId(courseId)} />
            </div>
          )
        ) : (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground mb-4">還沒有任何課程</p>
            <AddCourseDropdown
              onManualAdd={() => setShowCourseForm(true)}
              onGoogleClassroomImport={() => setShowGoogleClassroomImport(true)}
            />
          </Card>
        )}

        <GoogleClassroomImport
          isOpen={showGoogleClassroomImport}
          onClose={() => setShowGoogleClassroomImport(false)}
          onImport={handleBulkImport}
        />
      </>
    )
  }

  function TasksContent() {
    const handleAddCategory = (name: string, icon: string) => {
      if (!customCategories.some((cat) => (typeof cat === "string" ? cat === name : cat.name === name))) {
        // Store both name and icon for custom categories
        const newCategory = { name, icon }
        console.log("[v0] Adding new custom category:", name, icon)
        setCustomCategories([...customCategories, name]) // Keep string format for compatibility

        // Store the category with icon info in localStorage for TaskTypeToggle to access
        const storedCategoriesWithIcons = JSON.parse(localStorage.getItem("customCategoriesWithIcons") || "[]")
        const updatedCategoriesWithIcons = [...storedCategoriesWithIcons, newCategory]
        localStorage.setItem("customCategoriesWithIcons", JSON.stringify(updatedCategoriesWithIcons))

        setTaskType(name)
      }
    }

    const handleEditCategory = (oldName: string, newName: string, newIcon: string) => {
      // Update category name in the list
      setCustomCategories((prev) => prev.map((cat) => (cat === oldName ? newName : cat)))

      const storedCategoriesWithIcons = JSON.parse(localStorage.getItem("customCategoriesWithIcons") || "[]")
      const updatedCategoriesWithIcons = storedCategoriesWithIcons.map((cat: any) =>
        cat.name === oldName ? { name: newName, icon: newIcon } : cat,
      )
      localStorage.setItem("customCategoriesWithIcons", JSON.stringify(updatedCategoriesWithIcons))

      // Update all items in this category to use new name and icon
      setCustomCategoryItems((prev) =>
        prev.map((item) =>
          item.category === oldName ? { ...item, category: newName, icon: newIcon, updatedAt: new Date() } : item,
        ),
      )

      // Update current task type if it was the edited category
      if (taskType === oldName) {
        setTaskType(newName)
      }
    }

    const pendingAssignmentCount = assignments.filter((a) => a.status !== "completed").length
    const pendingExamCount = exams.filter((e) => e.status !== "completed").length

    const customCategoryData = customCategories.map((categoryName) => {
      const categoryItems = customCategoryItems.filter(
        (item) => item.category === categoryName && item.status !== "completed",
      )

      const storedCategoriesWithIcons = JSON.parse(localStorage.getItem("customCategoriesWithIcons") || "[]")
      const storedCategory = storedCategoriesWithIcons.find((cat: any) => cat.name === categoryName)
      const firstItem = customCategoryItems.find((item) => item.category === categoryName)
      const icon = storedCategory?.icon || firstItem?.icon || "clipboard"

      return {
        name: categoryName,
        icon,
        count: categoryItems.length,
      }
    })

    return (
      <>
        <PageHeader
          title="待辦事項"
          subtitle="追蹤你的作業與考試"
          action={
            <Button
              size="sm"
              onClick={() => {
                if (taskType === "assignment") {
                  setShowAssignmentForm(true)
                } else if (taskType === "exam") {
                  setShowExamForm(true)
                } else {
                  setShowCustomCategoryForm(true)
                }
              }}
            >
              <PlusIcon className="w-4 h-4 mr-1" />
              新增
            </Button>
          }
        />

        <TaskTypeToggle
          taskType={taskType}
          setTaskType={setTaskType}
          pendingAssignmentCount={pendingAssignmentCount}
          pendingExamCount={pendingExamCount}
          customCategoryData={customCategoryData}
          onAddCategory={handleAddCategory}
          onEditCategory={handleEditCategory}
          onDeleteCategory={handleDeleteCategory}
        />

        {taskType === "assignment" ? (
          <AssignmentsContent />
        ) : taskType === "exam" ? (
          <ExamsContent />
        ) : (
          <CustomCategoryContent />
        )}
      </>
    )
  }

  function CustomCategoryContent() {
    const filteredCustomCategoryItems = customCategoryItems.filter((item) => {
      if (taskType !== "all" && item.category !== taskType) {
        return false
      }

      const today = new Date()
      const daysUntilDue = getDaysDifferenceTaiwan(today, item.dueDate)
      const isOverdue = item.status === "overdue" || (item.status === "pending" && daysUntilDue < 0)

      // Update overdue status if needed
      if (item.status === "pending" && daysUntilDue < 0) {
        updateCustomCategoryItem(item.id, { status: "overdue" })
      }

      switch (customCategoryFilter) {
        case "pending":
          return item.status === "pending" && !isOverdue
        case "completed":
          return item.status === "completed"
        case "overdue":
          return item.status === "overdue" || isOverdue
        default:
          return true
      }
    })

    const sortedCustomCategoryItems = filteredCustomCategoryItems.sort((a, b) => {
      if (a.status === "overdue" && b.status !== "overdue") return -1
      if (b.status === "overdue" && a.status !== "overdue") return 1
      return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
    })

    const categoryItems =
      taskType === "all" ? customCategoryItems : customCategoryItems.filter((item) => item.category === taskType)

    const counts = {
      all: categoryItems.length,
      pending: categoryItems.filter((item) => {
        const today = new Date()
        const daysUntilDue = getDaysDifferenceTaiwan(today, item.dueDate)
        return item.status === "pending" && daysUntilDue >= 0
      }).length,
      completed: categoryItems.filter((item) => item.status === "completed").length,
      overdue: categoryItems.filter((item) => {
        const today = new Date()
        const daysUntilDue = getDaysDifferenceTaiwan(today, item.dueDate)
        return item.status === "overdue" || (item.status === "pending" && daysUntilDue < 0)
      }).length,
    }

    return (
      <>
        <CustomCategoryFilters
          activeFilter={customCategoryFilter}
          onFilterChange={setCustomCategoryFilter}
          counts={counts}
        />
        {sortedCustomCategoryItems.length > 0 && (
          <div className="space-y-3 pb-20 lg:pb-0">
            {sortedCustomCategoryItems.map((item) => (
              <CustomCategoryCard
                key={item.id}
                item={item}
                course={courses.find((c) => c.id === item.courseId)}
                onStatusChange={(id, status) => updateCustomCategoryItem(id, { status })}
                onViewDetail={() => {
                  setSelectedCustomCategoryId(item.id)
                }}
                onEdit={() => {
                  setEditingCustomCategory(item.id)
                  setShowCustomCategoryForm(true)
                }}
                onDelete={() => {
                  setCustomCategoryItems((prev) => prev.filter((i) => i.id !== item.id))
                  localStorage.setItem(
                    "customCategoryItems",
                    JSON.stringify(customCategoryItems.filter((i) => i.id !== item.id)),
                  )
                }}
              />
            ))}
          </div>
        )}
        {sortedCustomCategoryItems.length === 0 && (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground mb-4">
              {customCategoryFilter === "all"
                ? `還沒有任何${taskType}`
                : customCategoryFilter === "pending"
                  ? `沒有進行中的${taskType}`
                  : customCategoryFilter === "completed"
                    ? `沒有已完成的${taskType}`
                    : `沒有已逾期的${taskType}`}
            </p>
            {customCategoryFilter === "all" && (
              <Button onClick={() => setShowCustomCategoryForm(true)}>新增第一個{taskType}</Button>
            )}
          </Card>
        )}
      </>
    )
  }

  function AssignmentsContent() {
    const [, forceUpdate] = useState({})

    useEffect(() => {
      const interval = setInterval(() => {
        forceUpdate({})
      }, 10000) // Check every 10 seconds for immediate overdue detection

      return () => clearInterval(interval)
    }, [])

    useEffect(() => {
      const checkAssignmentStatus = () => {
        const taiwanNow = getTaiwanTime()

        assignments.forEach((assignment) => {
          const isOverdue = taiwanNow.getTime() > assignment.dueDate.getTime()

          console.log(
            "[v0] Assignment:",
            assignment.title,
            "Due:",
            assignment.dueDate,
            "Now:",
            taiwanNow,
            "IsOverdue:",
            isOverdue,
            "Status:",
            assignment.status,
          )

          if (assignment.status === "pending" && isOverdue) {
            updateAssignment(assignment.id, { status: "overdue" })
          } else if (assignment.status === "overdue" && !isOverdue) {
            // If assignment was overdue but due date was changed to future, make it pending again
            updateAssignment(assignment.id, { status: "pending" })
          }
        })
      }

      checkAssignmentStatus()
    }, [assignments, updateAssignment])

    const filteredAssignments = assignments.filter((assignment) => {
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
      all: assignments.length,
      pending: assignments.filter((a) => a.status === "pending").length,
      completed: assignments.filter((a) => a.status === "completed").length,
      overdue: assignments.filter((a) => a.status === "overdue").length,
    }

    return (
      <>
        <AssignmentFilters activeFilter={assignmentFilter} onFilterChange={setAssignmentFilter} counts={counts} />

        {sortedAssignments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-20 lg:pb-0">
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
            <p className="text-sm text-muted-foreground mb-2">
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
            <p className="text-sm text-muted-foreground mb-2">還沒有任何筆記</p>
            <Button onClick={() => setShowNoteForm(true)}>新增第一個筆記</Button>
          </Card>
        )}
      </>
    )
  }

  function ExamsContent() {
    const [, forceUpdate] = useState({})

    useEffect(() => {
      const interval = setInterval(() => {
        forceUpdate({})
      }, 10000) // Check every 10 seconds instead of 60 seconds

      return () => clearInterval(interval)
    }, [])

    useEffect(() => {
      const checkExamStatus = () => {
        exams.forEach((exam) => {
          const isEnded = isExamEndedTaiwan(exam.examDate, exam.duration)
          console.log(
            "[v0] Exam:",
            exam.title,
            "Date:",
            exam.examDate,
            "Duration:",
            exam.duration,
            "IsEnded:",
            isEnded,
            "Status:",
            exam.status,
          )

          if (exam.status === "pending" && isEnded) {
            updateExam(exam.id, { status: "overdue" })
          } else if (exam.status === "overdue" && !isEnded) {
            // If exam was overdue but date was changed to future, make it pending again
            updateExam(exam.id, { status: "pending" })
          }
        })
      }

      checkExamStatus()
    }, [exams, updateExam])

    const now = new Date()
    const oneWeekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

    const filteredExams = exams.filter((exam) => {
      const examDate = new Date(exam.examDate)

      switch (examFilter) {
        case "upcoming":
          return (
            examDate >= now && examDate <= oneWeekFromNow && exam.status !== "completed" && exam.status !== "overdue"
          )
        case "scheduled":
          return examDate > oneWeekFromNow && exam.status !== "completed" && exam.status !== "overdue"
        case "completed":
          return exam.status === "completed"
        case "overdue":
          return exam.status === "overdue"
        default:
          return true
      }
    })

    const sortedExams = filteredExams.sort((a, b) => {
      if (a.status === "overdue" && b.status !== "overdue") return -1
      if (b.status === "overdue" && a.status !== "overdue") return 1
      return new Date(a.examDate).getTime() - new Date(b.examDate).getTime()
    })

    const counts = {
      all: exams.length,
      upcoming: exams.filter((e) => {
        const examDate = new Date(e.examDate)
        return examDate >= now && examDate <= oneWeekFromNow && e.status !== "completed" && e.status !== "overdue"
      }).length,
      scheduled: exams.filter((e) => {
        const examDate = new Date(e.examDate)
        return examDate > oneWeekFromNow && e.status !== "completed" && e.status !== "overdue"
      }).length,
      completed: exams.filter((e) => e.status === "completed").length,
      overdue: exams.filter((e) => e.status === "overdue").length,
    }

    return (
      <>
        <ExamFilters activeFilter={examFilter} onFilterChange={setExamFilter} counts={counts} />

        {sortedExams.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-20 lg:pb-0">
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
                    : examFilter === "completed"
                      ? "沒有已結束的考試"
                      : "沒有已逾期的考試"}
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

  const handleBulkImport = (course: Omit<Course, "id" | "createdAt">) => {
    addCourse(course)
  }

  useEffect(() => {
    const handleSettingsChange = (event: CustomEvent) => {
      setNotificationSettings(event.detail)
    }

    window.addEventListener("notificationSettingsChanged", handleSettingsChange as EventListener)

    return () => {
      window.removeEventListener("notificationSettingsChanged", handleSettingsChange as EventListener)
    }
  }, [])

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const tab = urlParams.get("tab")
    const assignmentId = urlParams.get("assignment")
    const examId = urlParams.get("exam")

    if (tab) {
      setActiveTab(tab)
    }

    if (assignmentId) {
      setSelectedAssignmentId(assignmentId)
      setTaskType("assignment")
    }

    if (examId) {
      setSelectedExamId(examId)
      setTaskType("exam")
    }
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <SidebarNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="lg:ml-[var(--sidebar-width)] transition-[margin] duration-300">
        <div className="container mx-auto px-4 py-6 lg:max-w-7xl lg:px-12 lg:py-10">{renderContent()}</div>
      </div>

      <div className="lg:hidden">
        <BottomNavigation
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveTab(tab)
            if (tab === "home") {
              setSelectedDate(new Date())
            }
          }}
        />
      </div>

      <div className="lg:hidden">
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
          onAddCustomCategory={() => {
            setActiveTab("tasks")
            setShowCustomCategoryForm(true)
          }}
        />
      </div>
    </div>
  )
}
