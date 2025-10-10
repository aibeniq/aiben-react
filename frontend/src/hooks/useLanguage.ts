import { UsersService } from "@/client"
import useAuth from "@/hooks/useAuth"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

export const useLanguage = () => {
  const { i18n, t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [isUpdating, setIsUpdating] = useState(false)

  // Fetch supported languages from backend (for AI output translation)
  const { data: supportedLanguagesResponse, isLoading } = useQuery({
    queryKey: ["supportedLanguages"],
    queryFn: () => UsersService.getSupportedLanguages(),
  })

  // Extract the languages from the response
  const allSupportedLanguages =
    (supportedLanguagesResponse as any)?.languages || {}

  // Update language mutation that syncs with backend
  const updateLanguageMutation = useMutation({
    mutationFn: async (language: string) => {
      // Always change UI language - i18n will handle missing translations
      await i18n.changeLanguage(language)

      // Save to localStorage for persistence
      localStorage.setItem("preferredLanguage", language)
      localStorage.setItem("i18nextLng", language)

      // Always update backend preference (for AI output translation)
      return UsersService.updateLanguage({
        requestBody: { preferred_language: language },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
    onError: (error) => {
      console.error("Error updating language preference:", error)
      // Revert i18n change on error
      const userLanguage = user?.preferred_language || "en"
      i18n.changeLanguage(userLanguage)
    },
  })

  // Initialize language from user preference
  useEffect(() => {
    if (user?.preferred_language && user.preferred_language !== i18n.language) {
      i18n.changeLanguage(user.preferred_language)
    }
  }, [user, i18n])

  const changeLanguage = (language: string) => {
    setIsUpdating(true)
    updateLanguageMutation.mutate(language, {
      onSettled: () => setIsUpdating(false),
    })
  }

  return {
    currentLanguage: i18n.language,
    // Return all backend-supported languages for selection
    supportedLanguages: allSupportedLanguages,
    // All backend-supported languages (for AI output translation)
    allSupportedLanguages,
    // For backward compatibility - now returns all languages
    availableLanguages: allSupportedLanguages,
    changeLanguage,
    isUpdating: isUpdating || updateLanguageMutation.isPending,
    isLoading,
    t,
  }
}
