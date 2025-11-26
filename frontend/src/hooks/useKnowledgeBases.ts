import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { KnowledgeBasesService } from "../client"
import useAuth from "./useAuth"

interface UseKnowledgeBasesReturn {
  knowledgeBases: any[]
  isLoading: boolean
  showAllUsers: boolean
  toggleShowAllUsers: () => void
  canViewAllUsers: boolean
}

export const useKnowledgeBases = (): UseKnowledgeBasesReturn => {
  const { user: currentUser } = useAuth()
  const [showAllUsers, setShowAllUsers] = useState(false)
  
  const canViewAllUsers = currentUser?.is_superuser ?? false

  // Toggle handler for showing all users
  const toggleShowAllUsers = () => {
    console.log(
      "Knowledge Bases All Users toggle clicked. New value:",
      !showAllUsers,
    )
    setShowAllUsers((prev) => !prev)
  }

  // Knowledge bases query
  const knowledgeBasesQuery = useQuery({
    queryKey: ["knowledge-bases", showAllUsers],
    queryFn: async () => {
      console.log(
        "🔄 KNOWLEDGE-BASES: Starting to fetch knowledge bases, showAllUsers:",
        showAllUsers,
      )
      const response = await KnowledgeBasesService.readKnowledgeBases({
        limit: 1000, // Increased to fetch more records for proper pagination
        showAll: showAllUsers,
      })
      console.log("✅ KNOWLEDGE-BASES: Fetch completed, response:", response)
      console.log(
        "📊 KNOWLEDGE-BASES: Number of knowledge bases returned:",
        response?.data?.length || 0,
      )
      return response?.data || []
    },
    enabled: true,
  })

  return {
    knowledgeBases: knowledgeBasesQuery.data || [],
    isLoading: knowledgeBasesQuery.isLoading,
    showAllUsers,
    toggleShowAllUsers,
    canViewAllUsers,
  }
}
