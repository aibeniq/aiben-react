import { UsersService } from "@/client"
import { Radio, RadioGroup } from "@/components/ui/radio"
import useAuth from "@/hooks/useAuth"
import { Box, Card, Stack, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

const ProcessingDefaultsSettings = () => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
    (user?.default_processing_mode as "vector" | "full_scan") ?? "vector",
  )
  const [visionAnalysis, setVisionAnalysis] = useState(user?.vision_analysis_enabled ?? false)
  const [pdfParsing, setPdfParsing] = useState<"enhanced" | "basic">(
    (user?.pdf_parsing_preference as "enhanced" | "basic") ?? "basic",
  )

  // Sync local state with user data when it changes
  useEffect(() => {
    if (user?.default_processing_mode !== undefined) {
      setSearchMode(user.default_processing_mode as "vector" | "full_scan")
    }
    if (user?.vision_analysis_enabled !== undefined) {
      setVisionAnalysis(user.vision_analysis_enabled)
    }
    if (user?.pdf_parsing_preference !== undefined) {
      setPdfParsing(user.pdf_parsing_preference as "enhanced" | "basic")
    }
  }, [user?.default_processing_mode, user?.vision_analysis_enabled, user?.pdf_parsing_preference])

  const updateMutation = useMutation({
    mutationFn: (settings: {
      default_processing_mode: string
      vision_analysis_enabled: boolean
      pdf_parsing_preference: string
    }) => {
      console.log("[ProcessingDefaults] Sending update:", settings)
      return UsersService.updateProcessingDefaults({
        requestBody: settings,
      })
    },
    onSuccess: async (data) => {
      console.log("[ProcessingDefaults] Update successful, response:", data)
      // Update the cache with the response data
      queryClient.setQueryData(["currentUser"], data)
      // Also invalidate to ensure fresh data
      await queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const handleSearchModeChange = (newMode: "vector" | "full_scan") => {
    setSearchMode(newMode)
    updateMutation.mutate({
      default_processing_mode: newMode,
      vision_analysis_enabled: visionAnalysis,
      pdf_parsing_preference: pdfParsing,
    })
  }

  const handleVisionAnalysisChange = (checked: boolean) => {
    setVisionAnalysis(checked)
    updateMutation.mutate({
      default_processing_mode: searchMode,
      vision_analysis_enabled: checked,
      pdf_parsing_preference: pdfParsing,
    })
  }

  const handlePdfParsingChange = (newMode: "enhanced" | "basic") => {
    setPdfParsing(newMode)
    updateMutation.mutate({
      default_processing_mode: searchMode,
      vision_analysis_enabled: visionAnalysis,
      pdf_parsing_preference: newMode,
    })
  }

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={6}>
          {/* Header */}
          <Box>
            <Text fontSize="lg" fontWeight="semibold">
              {t("settings.processingDefaults.title")}
            </Text>
            <Text fontSize="sm" color="gray.600" mt={2}>
              {t("settings.processingDefaults.description")}
            </Text>
          </Box>

          <Box p={3} bg="blue.50" borderRadius="md" borderLeft="4px solid" borderColor="blue.500">
            <Text fontSize="sm">{t("settings.processingDefaults.explanation")}</Text>
          </Box>

          {/* Search Mode */}
          <Box>
            <Text fontSize="md" fontWeight="semibold" mb={3}>
              {t("settings.processingDefaults.searchMode")}
            </Text>
            <RadioGroup
              value={searchMode}
              onValueChange={(details) =>
                handleSearchModeChange(details.value as "vector" | "full_scan")
              }
            >
              <Stack gap={4}>
                <Radio value="vector" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">
                      {t("settings.processingDefaults.vectorSearch")}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.processingDefaults.vectorSearchDescription")}
                    </Text>
                  </Box>
                </Radio>

                <Radio value="full_scan" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">
                      {t("settings.processingDefaults.fullDocumentScan")}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.processingDefaults.fullScanDescription")}
                    </Text>
                  </Box>
                </Radio>
              </Stack>
            </RadioGroup>
          </Box>

          {/* Vision Analysis */}
          <Box>
            <Text fontSize="md" fontWeight="semibold" mb={3}>
              {t("settings.processingDefaults.visionAnalysis")}
            </Text>
            <RadioGroup
              value={visionAnalysis ? "enabled" : "disabled"}
              onValueChange={(details) => handleVisionAnalysisChange(details.value === "enabled")}
            >
              <Stack gap={4}>
                <Radio value="enabled" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">
                      {t("settings.processingDefaults.visionEnabled")}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.processingDefaults.visionEnabledDescription")}
                    </Text>
                  </Box>
                </Radio>

                <Radio value="disabled" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">
                      {t("settings.processingDefaults.visionDisabled")}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.processingDefaults.visionDisabledDescription")}
                    </Text>
                  </Box>
                </Radio>
              </Stack>
            </RadioGroup>
            <Box
              p={3}
              bg="yellow.50"
              borderRadius="md"
              borderLeft="4px solid"
              borderColor="yellow.500"
              mt={3}
            >
              <Text fontSize="sm">{t("settings.processingDefaults.visionCostWarning")}</Text>
            </Box>
          </Box>

          {/* PDF Parsing */}
          <Box>
            <Text fontSize="md" fontWeight="semibold" mb={3}>
              {t("settings.processingDefaults.pdfParsing")}
            </Text>
            <RadioGroup
              value={pdfParsing}
              onValueChange={(details) =>
                handlePdfParsingChange(details.value as "enhanced" | "basic")
              }
            >
              <Stack gap={4}>
                <Radio value="enhanced" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">
                      {t("settings.processingDefaults.enhancedParsing")}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.processingDefaults.enhancedParsingDescription")}
                    </Text>
                  </Box>
                </Radio>

                <Radio value="basic" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">
                      {t("settings.processingDefaults.basicParsing")}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.processingDefaults.basicParsingDescription")}
                    </Text>
                  </Box>
                </Radio>
              </Stack>
            </RadioGroup>
          </Box>

          {/* Comparison Info */}
          <Box fontSize="xs" color="gray.500" bg="gray.50" p={4} borderRadius="md">
            <Text fontWeight="semibold" mb={3}>
              {t("settings.processingDefaults.comparison.title")}
            </Text>

            <VStack align="start" gap={3}>
              <Box>
                <Text fontWeight="semibold" color="blue.600" mb={1}>
                  {t("settings.processingDefaults.comparison.vectorTitle")}
                </Text>
                <Text>✓ {t("settings.processingDefaults.comparison.vectorFeature1")}</Text>
                <Text>✓ {t("settings.processingDefaults.comparison.vectorFeature2")}</Text>
              </Box>

              <Box>
                <Text fontWeight="semibold" color="green.600" mb={1}>
                  {t("settings.processingDefaults.comparison.fullScanTitle")}
                </Text>
                <Text>✓ {t("settings.processingDefaults.comparison.fullScanFeature1")}</Text>
                <Text>⚠ {t("settings.processingDefaults.comparison.fullScanWarning")}</Text>
              </Box>
            </VStack>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default ProcessingDefaultsSettings
