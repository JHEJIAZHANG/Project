"use client"

import { useState, useEffect } from "react"

export interface CustomCategory {
  id: string
  name: string
  icon: string
  color: string
  createdAt: Date
}

export function useCustomCategories() {
  const [categories, setCategories] = useState<CustomCategory[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Load categories from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem("customCategories")
      if (stored) {
        const parsed = JSON.parse(stored)
        const categoriesWithDates = parsed.map((cat: any) => ({
          ...cat,
          createdAt: new Date(cat.createdAt),
        }))
        setCategories(categoriesWithDates)
      } else {
        // Initialize with default categories
        const defaultCategories: CustomCategory[] = [
          {
            id: "study",
            name: "學習",
            icon: "book",
            color: "#3b82f6",
            createdAt: new Date(),
          },
          {
            id: "project",
            name: "專案",
            icon: "clipboard",
            color: "#10b981",
            createdAt: new Date(),
          },
          {
            id: "personal",
            name: "個人",
            icon: "heart",
            color: "#f59e0b",
            createdAt: new Date(),
          },
        ]
        setCategories(defaultCategories)
        localStorage.setItem("customCategories", JSON.stringify(defaultCategories))
      }
    } catch (error) {
      console.error("Error loading custom categories:", error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Save categories to localStorage whenever they change
  useEffect(() => {
    if (!isLoading) {
      localStorage.setItem("customCategories", JSON.stringify(categories))
    }
  }, [categories, isLoading])

  const addCategory = (category: Omit<CustomCategory, "id" | "createdAt">) => {
    const newCategory: CustomCategory = {
      ...category,
      id: Date.now().toString(),
      createdAt: new Date(),
    }
    setCategories((prev) => [...prev, newCategory])
    return newCategory
  }

  const updateCategory = (id: string, updates: Partial<Omit<CustomCategory, "id" | "createdAt">>) => {
    setCategories((prev) => prev.map((cat) => (cat.id === id ? { ...cat, ...updates } : cat)))
  }

  const deleteCategory = (id: string) => {
    setCategories((prev) => prev.filter((cat) => cat.id !== id))
  }

  const getCategoryById = (id: string) => {
    return categories.find((cat) => cat.id === id)
  }

  return {
    categories,
    isLoading,
    addCategory,
    updateCategory,
    deleteCategory,
    getCategoryById,
  }
}
