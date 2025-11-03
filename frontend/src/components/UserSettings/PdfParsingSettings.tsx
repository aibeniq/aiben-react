import { Field } from "@/components/ui/field"
import { Radio, RadioGroup } from "@/components/ui/radio"
import { Box, Card, VStack, Text, Stack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { UsersService } from "@/client"
import useAuth from "@/hooks/useAuth"
import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"

const PdfParsingSettings = () => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [mode, setMode] = useState(user?.pdf_parsing_preference ?? "basic")

  // Sync local state with user data when it changes
  useEffect(() => {
    if (user?.pdf_parsing_preference !== undefined) {
      console.log("[PdfParsing] Syncing state from user:", user.pdf_parsing_preference)
      console.log("[PdfParsing] Current local mode:", mode)
      setMode(user.pdf_parsing_preference)
    }
  }, [user?.pdf_parsing_preference])

  // Debug: Log when component mounts/updates
  useEffect(() => {
    console.log(
      "[PdfParsing] Component rendered. User preference:",
      user?.pdf_parsing_preference,
      "Local mode:",
      mode,
    )
  })

  const updateMutation = useMutation({
    mutationFn: (parsingMode: string) => {
      console.log("[PdfParsing] Sending update:", parsingMode)
      return UsersService.updatePdfParsingPreference({
        requestBody: { pdf_parsing_preference: parsingMode },
      })
    },
    onSuccess: async (data) => {
      console.log("[PdfParsing] Update successful, response:", data)
      // Update the cache with the response data
      queryClient.setQueryData(["currentUser"], data)
      // Also invalidate to ensure fresh data
      await queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const handleModeChange = (details: { value: string | null }) => {
    if (!details.value) return
    const newMode = details.value
    console.log("[PdfParsing] Mode changed, current:", mode, "new:", newMode)
    setMode(newMode)
    updateMutation.mutate(newMode)
  }

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={4}>
          <Box>
            <Text fontSize="lg" fontWeight="semibold">
              {t("settings.pdfParsing.title")}
            </Text>
            <Text fontSize="sm" color="gray.600" mt={2}>
              {t("settings.pdfParsing.description")}
            </Text>
          </Box>

          <Box p={3} bg="blue.50" borderRadius="md" borderLeft="4px solid" borderColor="blue.500">
            <Text fontSize="sm">{t("settings.pdfParsing.explanation")}</Text>
          </Box>

          <Field label={t("settings.pdfParsing.modeLabel") as string}>
            <RadioGroup value={mode} onValueChange={handleModeChange}>
              <Stack gap={4}>
                <Radio value="basic" disabled={updateMutation.isPending}>
                  <VStack align="start" gap={1}>
                    <Text fontWeight="semibold">{t("settings.pdfParsing.basicMode")}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.pdfParsing.basicDescription")}
                    </Text>
                  </VStack>
                </Radio>

                <Radio value="enhanced" disabled={updateMutation.isPending}>
                  <VStack align="start" gap={1}>
                    <Text fontWeight="semibold">{t("settings.pdfParsing.enhancedMode")}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.pdfParsing.enhancedDescription")}
                    </Text>
                  </VStack>
                </Radio>
              </Stack>
            </RadioGroup>
          </Field>

          <Box fontSize="xs" color="gray.500" bg="gray.50" p={4} borderRadius="md">
            <Text fontWeight="semibold" mb={3}>
              {t("settings.pdfParsing.comparison.title")}
            </Text>

            <VStack align="start" gap={3}>
              <Box>
                <Text fontWeight="semibold" color="purple.600" mb={1}>
                  {t("settings.pdfParsing.comparison.basicTitle")}
                </Text>
                <Text>✓ {t("settings.pdfParsing.comparison.basicFeature1")}</Text>
                <Text>✓ {t("settings.pdfParsing.comparison.basicFeature2")}</Text>
                <Text>⚠ {t("settings.pdfParsing.comparison.basicWarning")}</Text>
              </Box>
              <Box>
                <Text fontWeight="semibold" color="green.600" mb={1}>
                  {t("settings.pdfParsing.comparison.enhancedTitle")}
                </Text>
                <Text>✓ {t("settings.pdfParsing.comparison.enhancedFeature1")}</Text>
                <Text>✓ {t("settings.pdfParsing.comparison.enhancedFeature2")}</Text>
                <Text>⚠ {t("settings.pdfParsing.comparison.enhancedWarning")}</Text>
              </Box>
            </VStack>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default PdfParsingSettings
