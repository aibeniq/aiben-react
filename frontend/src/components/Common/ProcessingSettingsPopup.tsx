import { Box, Button, HStack, IconButton, Portal, Text, VStack } from "@chakra-ui/react"
import { useState } from "react"
import { useEffect, useRef } from "react"
import { useTranslation } from "react-i18next"
import { FiSettings } from "react-icons/fi"
import {
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
  /**
   * z-index to apply to the dialog content so the popup can appear above other modals.
   * Defaults to 20000 which is above everything else in the app (chat is 9999).
   * This applies to the portal container itself.
   */
  contentZIndex?: number
  /**
   * Optional z-index for the backdrop element rendered by this popup.
   * Allows parent dialogs to control stacking of the semi-opaque backdrop.
   */
  backdropZIndex?: number
}

const ProcessingSettingsPopup = ({
  settings,
  onSettingsChange,
  disabled = false,
  contentZIndex = 20000,
  backdropZIndex,
}: ProcessingSettingsPopupProps) => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [tempSettings, setTempSettings] = useState<ProcessingSettings>(settings)
  const [suppressBackdrop, setSuppressBackdrop] = useState(false)
  const portalRef = useRef<HTMLElement | null>(null)

  // Ensure a dedicated top-level portal container exists so this popup renders
  // above other modal portals regardless of render order. We create an element
  // with a very high z-index and append it to document.body.
  useEffect(() => {
    const id = "top-processing-settings-portal"
    let el = document.getElementById(id) as HTMLElement | null
    if (!el) {
      el = document.createElement("div")
      el.id = id
      // position and zIndex help create a stacking context above other elements
      el.style.position = "fixed"
      el.style.top = "0"
      el.style.left = "0"
      el.style.width = "100%"
      el.style.height = "100%"
      // Never capture pointer events on the container itself - let child elements handle it
      el.style.pointerEvents = "none"
      // Ensure we're not trapped in a stacking context
      el.style.isolation = "auto"
      document.body.appendChild(el)
    }
    // Always update the z-index to ensure it's on top, using a very high value
    // that's guaranteed to be above everything else (including chat at 9999)
    el.style.zIndex = String(Math.max(contentZIndex, 20000))
    portalRef.current = el
    // Keep the portal element persistent (don't remove on unmount) to avoid
    // race conditions if multiple components mount/unmount.
  }, [contentZIndex, isOpen]) // Re-run when contentZIndex or isOpen changes

  const handleOpen = () => {
    setTempSettings(settings) // Reset to current settings
    // Detect if another dialog is already open in the document. If so,
    // we'll suppress the backdrop for this popup to avoid double-overlaying
    // and blocking interaction.
    const existingDialogs = document.querySelectorAll('[role="dialog"]')
    const hasOtherDialogOpen = existingDialogs && existingDialogs.length > 0
    setSuppressBackdrop(hasOtherDialogOpen)
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

      {isOpen && (
        <Portal container={portalRef}>
          {/* Custom backdrop to ensure it covers everything underneath */}
          {!suppressBackdrop && (
            <Box
              position="fixed"
              top={0}
              left={0}
              width="100vw"
              height="100vh"
              bg="blackAlpha.600"
              zIndex={backdropZIndex ?? 1}
              onClick={handleClose}
              style={{
                pointerEvents: "auto",
              }}
            />
          )}
          <DialogRoot open={isOpen} onOpenChange={(e) => !e.open && handleClose()} size="lg">
            <DialogContent
              portalled={false}
              backdrop={false}
              style={{ zIndex: (backdropZIndex ?? 1) + 1 }}
            >
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
                      <HStack align="start" gap={4}>
                        <Radio value="vector" flex={1}>
                          <Box>
                            <Text fontWeight="semibold">
                              {t("processingSettings.vectorSearch")}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {t("processingSettings.vectorSearchDescription")}
                            </Text>
                          </Box>
                        </Radio>
                        <Radio value="full_scan" flex={1}>
                          <Box>
                            <Text fontWeight="semibold">
                              {t("processingSettings.fullDocumentScan")}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {t("processingSettings.fullScanDescription")}
                            </Text>
                          </Box>
                        </Radio>
                      </HStack>
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
                      <HStack align="start" gap={4}>
                        <Radio value="enabled" flex={1}>
                          <Box>
                            <Text fontWeight="semibold">
                              {t("processingSettings.visionEnabled")}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {t("processingSettings.visionEnabledDescription")}
                            </Text>
                          </Box>
                        </Radio>
                        <Radio value="disabled" flex={1}>
                          <Box>
                            <Text fontWeight="semibold">
                              {t("processingSettings.visionDisabled")}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {t("processingSettings.visionDisabledDescription")}
                            </Text>
                          </Box>
                        </Radio>
                      </HStack>
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
                      <HStack align="start" gap={4}>
                        <Radio value="enhanced" flex={1}>
                          <Box>
                            <Text fontWeight="semibold">
                              {t("processingSettings.enhancedParsing")}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {t("processingSettings.enhancedParsingDescription")}
                            </Text>
                          </Box>
                        </Radio>
                        <Radio value="basic" flex={1}>
                          <Box>
                            <Text fontWeight="semibold">
                              {t("processingSettings.basicParsing")}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {t("processingSettings.basicParsingDescription")}
                            </Text>
                          </Box>
                        </Radio>
                      </HStack>
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
          </DialogRoot>
        </Portal>
      )}
    </>
  )
}

export default ProcessingSettingsPopup
