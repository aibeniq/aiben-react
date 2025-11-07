import { UsersService } from "@/client"
import { Field } from "@/components/ui/field"
import useAuth from "@/hooks/useAuth"
import { Box, Card, Switch, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

const VisionAnalysisSettings = () => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [enabled, setEnabled] = useState(user?.vision_analysis_enabled ?? false)

  // Sync local state with user data when it changes
  useEffect(() => {
    if (user?.vision_analysis_enabled !== undefined) {
      console.log("[VisionAnalysis] Syncing state from user:", user.vision_analysis_enabled)
      setEnabled(user.vision_analysis_enabled)
    }
  }, [user?.vision_analysis_enabled])

  const updateMutation = useMutation({
    mutationFn: (visionEnabled: boolean) => {
      console.log("[VisionAnalysis] Sending update:", visionEnabled)
      return UsersService.updateVisionAnalysisSetting({
        requestBody: { vision_analysis_enabled: visionEnabled },
      })
    },
    onSuccess: (data) => {
      console.log("[VisionAnalysis] Update successful, response:", data)
      // Update the cache with the response data from the server
      queryClient.setQueryData(["currentUser"], data)
    },
  })

  const handleToggle = () => {
    const newValue = !enabled
    console.log("[VisionAnalysis] Toggle clicked, current:", enabled, "new:", newValue)
    setEnabled(newValue)
    updateMutation.mutate(newValue)
  }

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={4}>
          <Box>
            <Text fontSize="lg" fontWeight="semibold">
              {t("settings.visionAnalysis.title")}
            </Text>
            <Text fontSize="sm" color="gray.600" mt={2}>
              {t("settings.visionAnalysis.description")}
            </Text>
          </Box>

          <Box p={3} bg="blue.50" borderRadius="md" borderLeft="4px solid" borderColor="blue.500">
            <Text fontSize="sm">{t("settings.visionAnalysis.costWarning")}</Text>
          </Box>

          <Field label={t("settings.visionAnalysis.enableLabel") as string}>
            <Switch.Root
              size="md"
              colorPalette="blue"
              checked={enabled}
              disabled={updateMutation.isPending}
            >
              <Switch.HiddenInput checked={enabled} onChange={handleToggle} />
              <Switch.Control>
                <Switch.Thumb />
              </Switch.Control>
            </Switch.Root>
          </Field>

          <Box fontSize="xs" color="gray.500">
            <Text fontWeight="semibold" mb={2}>
              {t("settings.visionAnalysis.whenEnabled")}
            </Text>
            <VStack align="start" gap={1} pl={4}>
              <Text>• {t("settings.visionAnalysis.feature1")}</Text>
              <Text>• {t("settings.visionAnalysis.feature2")}</Text>
              <Text>• {t("settings.visionAnalysis.feature3")}</Text>
              <Text>• {t("settings.visionAnalysis.feature4")}</Text>
            </VStack>

            <Text fontWeight="semibold" mt={3} mb={2}>
              {t("settings.visionAnalysis.whenDisabled")}
            </Text>
            <VStack align="start" gap={1} pl={4}>
              <Text>• {t("settings.visionAnalysis.disabled1")}</Text>
              <Text>• {t("settings.visionAnalysis.disabled2")}</Text>
            </VStack>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default VisionAnalysisSettings
