import React from "react"
import { Card, VStack, Box } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import useAuth from "@/hooks/useAuth"
import { Field } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import useCustomToast from "@/hooks/useCustomToast"
import { UsersService, type ApiError } from "@/client"
import { handleError } from "@/utils"

// Default fallback languages (should match backend config)
const DEFAULT_LANGUAGES = [
  { code: "ar", name: "Arabic" },
  { code: "bg", name: "Bulgarian" },
  { code: "zh", name: "Chinese (Simplified)" },
  { code: "zh-TW", name: "Chinese (Traditional)" },
  { code: "hr", name: "Croatian" },
  { code: "cs", name: "Czech" },
  { code: "da", name: "Danish" },
  { code: "nl", name: "Dutch" },
  { code: "en", name: "English" },
  { code: "et", name: "Estonian" },
  { code: "tl", name: "Filipino" },
  { code: "fi", name: "Finnish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "el", name: "Greek" },
  { code: "he", name: "Hebrew" },
  { code: "hi", name: "Hindi" },
  { code: "hu", name: "Hungarian" },
  { code: "id", name: "Indonesian" },
  { code: "it", name: "Italian" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "lv", name: "Latvian" },
  { code: "lt", name: "Lithuanian" },
  { code: "ms", name: "Malay" },
  { code: "no", name: "Norwegian" },
  { code: "fa", name: "Persian (Farsi)" },
  { code: "pl", name: "Polish" },
  { code: "pt", name: "Portuguese" },
  { code: "pt-BR", name: "Portuguese (Brazil)" },
  { code: "ro", name: "Romanian" },
  { code: "ru", name: "Russian" },
  { code: "sr", name: "Serbian" },
  { code: "sk", name: "Slovak" },
  { code: "sl", name: "Slovenian" },
  { code: "es", name: "Spanish (Europe)" },
  { code: "es-LATAM", name: "Spanish (Latin America)" },
  { code: "sw", name: "Swahili" },
  { code: "sv", name: "Swedish" },
  { code: "th", name: "Thai" },
  { code: "tr", name: "Turkish" },
  { code: "uk", name: "Ukrainian" },
  { code: "vi", name: "Vietnamese" },
]

const LanguageSettings: React.FC = () => {
  const { user } = useAuth()
  const { showSuccessToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Default to English if the preferred_language isn't in the user object yet
  const currentLanguage =
    user && "preferred_language" in user ? String(user.preferred_language) : "en"
  const [selectedLanguage, setSelectedLanguage] = React.useState(currentLanguage)

  const updateLanguage = useMutation({
    mutationFn: async (language: string) => {
      return UsersService.updateLanguage({
        requestBody: { preferred_language: language },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      showSuccessToast("Your preferred language has been updated.")
    },
    onError: (error: ApiError) => {
      console.error("Language update error:", error)
      handleError(error)
    },
  })

  const handleSave = () => {
    updateLanguage.mutate(selectedLanguage)
  }

  const handleLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedLanguage(event.target.value)
  }

  return (
    <Card.Root p={4}>
      <Card.Body>
        <VStack gap={6} align="stretch">
          <Field label="Preferred Language">
            <select
              value={selectedLanguage}
              onChange={handleLanguageChange}
              className="chakra-select"
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "0.375rem",
                border: "1px solid",
                borderColor: "inherit",
              }}
            >
              {DEFAULT_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </Field>

          <Box>
            <Button
              colorPalette="blue"
              loading={updateLanguage.isPending}
              onClick={handleSave}
              disabled={selectedLanguage === currentLanguage}
            >
              Save Language Preference
            </Button>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default LanguageSettings
