import { Box, Button, HStack, IconButton, Portal, Stack, Text, VStack } from "@chakra-ui/react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { FiSettings } from "react-icons/fi"
import {
  DialogBackdrop,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "../ui/dialog"
import { Radio, RadioGroup } from "../ui/radio"

export interface ProcessingSettings {
  searchMode: "vector" | "full_scan"
  visionAnalysis: boolean
  pdfParsing: "enhanced" | "basic"
}

interface ProcessingSettingsPopupProps {
  settings: ProcessingSettings
  onSettingsChange: (settings: ProcessingSettings) => void
  disabled?: boolean
}

const ProcessingSettingsPopup = ({
  settings,
  onSettingsChange,
  disabled = false,
}: ProcessingSettingsPopupProps) => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [tempSettings, setTempSettings] = useState<ProcessingSettings>(settings)

  const handleOpen = () => {
    setTempSettings(settings) // Reset to current settings
    setIsOpen(true)
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  const handleApply = () => {
    onSettingsChange(tempSettings)
    setIsOpen(false)
  }

  return (
    <>
      <IconButton
        aria-label={t("processingSettings.configure")}
        variant="ghost"
        size="sm"
        onClick={handleOpen}
        disabled={disabled}
      >
        <FiSettings />
      </IconButton>

      <DialogRoot open={isOpen} onOpenChange={(e) => setIsOpen(e.open)} size="lg">
        <Portal>
          <DialogBackdrop />
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("processingSettings.title")}</DialogTitle>
              <DialogCloseTrigger />
            </DialogHeader>

            <DialogBody>
              <VStack align="stretch" gap={6}>
                {/* Search Mode */}
                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    {t("processingSettings.searchMode")}
                  </Text>
                  <RadioGroup
                    value={tempSettings.searchMode}
                    onValueChange={(details) =>
                      setTempSettings({
                        ...tempSettings,
                        searchMode: details.value as "vector" | "full_scan",
                      })
                    }
                  >
                    <Stack gap={3}>
                      <Radio value="vector">
                        <Box>
                          <Text fontWeight="semibold">{t("processingSettings.vectorSearch")}</Text>
                          <Text fontSize="xs" color="gray.600">
                            {t("processingSettings.vectorSearchDescription")}
                          </Text>
                        </Box>
                      </Radio>
                      <Radio value="full_scan">
                        <Box>
                          <Text fontWeight="semibold">
                            {t("processingSettings.fullDocumentScan")}
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            {t("processingSettings.fullScanDescription")}
                          </Text>
                        </Box>
                      </Radio>
                    </Stack>
                  </RadioGroup>
                </Box>

                {/* Vision Analysis */}
                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    {t("processingSettings.visionAnalysis")}
                  </Text>
                  <RadioGroup
                    value={tempSettings.visionAnalysis ? "enabled" : "disabled"}
                    onValueChange={(details) =>
                      setTempSettings({
                        ...tempSettings,
                        visionAnalysis: details.value === "enabled",
                      })
                    }
                  >
                    <Stack gap={3}>
                      <Radio value="enabled">
                        <Box>
                          <Text fontWeight="semibold">{t("processingSettings.visionEnabled")}</Text>
                          <Text fontSize="xs" color="gray.600">
                            {t("processingSettings.visionEnabledDescription")}
                          </Text>
                        </Box>
                      </Radio>
                      <Radio value="disabled">
                        <Box>
                          <Text fontWeight="semibold">
                            {t("processingSettings.visionDisabled")}
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            {t("processingSettings.visionDisabledDescription")}
                          </Text>
                        </Box>
                      </Radio>
                    </Stack>
                  </RadioGroup>
                </Box>

                {/* PDF Parsing */}
                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    {t("processingSettings.pdfParsing")}
                  </Text>
                  <RadioGroup
                    value={tempSettings.pdfParsing}
                    onValueChange={(details) =>
                      setTempSettings({
                        ...tempSettings,
                        pdfParsing: details.value as "enhanced" | "basic",
                      })
                    }
                  >
                    <Stack gap={3}>
                      <Radio value="enhanced">
                        <Box>
                          <Text fontWeight="semibold">
                            {t("processingSettings.enhancedParsing")}
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            {t("processingSettings.enhancedParsingDescription")}
                          </Text>
                        </Box>
                      </Radio>
                      <Radio value="basic">
                        <Box>
                          <Text fontWeight="semibold">{t("processingSettings.basicParsing")}</Text>
                          <Text fontSize="xs" color="gray.600">
                            {t("processingSettings.basicParsingDescription")}
                          </Text>
                        </Box>
                      </Radio>
                    </Stack>
                  </RadioGroup>
                </Box>

                <Box
                  p={3}
                  bg="blue.50"
                  borderRadius="md"
                  borderLeft="4px solid"
                  borderColor="blue.500"
                >
                  <Text fontSize="xs">{t("processingSettings.overrideNote")}</Text>
                </Box>
              </VStack>
            </DialogBody>

            <DialogFooter>
              <HStack gap={2}>
                <Button variant="outline" onClick={handleClose}>
                  {t("buttons.cancel")}
                </Button>
                <Button colorPalette="blue" onClick={handleApply}>
                  {t("buttons.apply")}
                </Button>
              </HStack>
            </DialogFooter>
          </DialogContent>
        </Portal>
      </DialogRoot>
    </>
  )
}

export default ProcessingSettingsPopup
