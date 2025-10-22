import {
  Box,
  Button,
  Dialog,
  HStack,
  IconButton,
  Portal,
  Spinner,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import { FiCheck, FiEdit3, FiSave, FiX } from "react-icons/fi"
import {
  type CancelablePromise,
  type ChecklistSuggestion,
  type VeraDocChecklist,
  VeradocService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import FileUpload, { type FileItem } from "../Common/FileUpload"
import SearchModeToggle from "../Common/SearchModeToggle"
import { Field } from "../ui/field"

interface OptimizeChecklistModalProps {
  isOpen: boolean
  onClose: () => void
  checklist: VeraDocChecklist | null
  selectedKnowledgeBase: any
  onOptimized: (optimizedQuestions: string[]) => void
}

const OptimizeChecklistModal: React.FC<OptimizeChecklistModalProps> = ({
  isOpen,
  onClose,
  checklist,
  selectedKnowledgeBase,
  onOptimized,
}) => {
  const { t } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [fileItems, setFileItems] = useState<FileItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<ChecklistSuggestion[]>([])
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set())
  const [isApplying, setIsApplying] = useState(false)
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")
  const [customInstructions, setCustomInstructions] = useState("")
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)
  const [editingSuggestions, setEditingSuggestions] = useState<Map<number, string>>(new Map())
  const [editingModes, setEditingModes] = useState<Set<number>>(new Set())
  const [hasOptimized, setHasOptimized] = useState(false)
  const [expandedAnswers, setExpandedAnswers] = useState<Set<number>>(new Set())

  // Add cancelable promise ref for request cancellation
  const ongoingRequestRef = useRef<CancelablePromise<any> | null>(null)

  const handleOptimize = async () => {
    if (!checklist) {
      showErrorToast(t("toast.noChecklistForOptimization"))
      return
    }

    if (!selectedKnowledgeBase) {
      showErrorToast(t("toast.selectKnowledgeBaseFirst"))
      return
    }

    if (!checklist.questions || checklist.questions.trim() === "") {
      showErrorToast(t("toast.provideChecklistQuestions"))
      return
    }

    if (fileItems.length === 0 || !fileItems.some((item) => item.file.size > 0)) {
      showErrorToast(t("toast.uploadAcceptedDocuments"))
      return
    }

    // Cancel any existing request
    if (ongoingRequestRef.current) {
      ongoingRequestRef.current.cancel()
      ongoingRequestRef.current = null
    }

    setIsLoading(true)
    try {
      const validItems = fileItems.filter((item) => item.file.size > 0)
      const files = validItems.map((item) => item.file)

      // Store the cancelable promise
      ongoingRequestRef.current = VeradocService.optimizeChecklist({
        knowledgeBaseId: selectedKnowledgeBase.id,
        questions: checklist.questions || "",
        customInstructions: customInstructions || undefined,
        searchMode: searchMode === "full_scan" ? "full_text" : searchMode,
        formData: {
          files: files,
        },
      })

      const response = await ongoingRequestRef.current

      // Clear the reference on successful completion
      ongoingRequestRef.current = null

      console.log("Optimization response:", response)

      if (response.suggestions && response.suggestions.length > 0) {
        const optimizationCount = response.suggestions.filter(
          (s: ChecklistSuggestion) => s.needs_revision,
        ).length
        setSuggestions(response.suggestions)
        setHasOptimized(true)
        showSuccessToast(
          t("optimizeChecklistModal.analysisComplete", {
            count: optimizationCount,
            total: response.suggestions.length,
          }),
        )
      } else {
        showSuccessToast(t("optimizeChecklistModal.noOptimizationSuggestions"))
        setSuggestions([])
      }
    } catch (error: any) {
      // Don't show error if request was cancelled
      if (error.isCancelled || error.name === "CancelError") {
        console.log("Optimization request was cancelled")
        return
      }

      console.error("Optimization error:", error)
      showErrorToast(t("toast.optimizeChecklistFailed"))
    } finally {
      setIsLoading(false)
      ongoingRequestRef.current = null
    }
  }

  const handleSuggestionToggle = (index: number) => {
    const newAccepted = new Set(acceptedSuggestions)
    if (newAccepted.has(index)) {
      newAccepted.delete(index)
    } else {
      newAccepted.add(index)
    }
    setAcceptedSuggestions(newAccepted)
  }

  const handleEditSuggestion = (index: number) => {
    const suggestion = suggestions[index]
    if (suggestion) {
      setEditingSuggestions(
        new Map(editingSuggestions.set(index, suggestion.suggested_question || "")),
      )
      setEditingModes(new Set(editingModes.add(index)))
    }
  }

  const handleSaveSuggestion = (index: number) => {
    const editedText = editingSuggestions.get(index)
    if (editedText !== undefined) {
      const updatedSuggestions = [...suggestions]
      updatedSuggestions[index] = {
        ...updatedSuggestions[index],
        suggested_question: editedText,
      }
      setSuggestions(updatedSuggestions)
      setEditingModes(new Set([...editingModes].filter((i) => i !== index)))
    }
  }

  const handleCancelEdit = (index: number) => {
    setEditingModes(new Set([...editingModes].filter((i) => i !== index)))
    setEditingSuggestions(new Map([...editingSuggestions].filter(([i]) => i !== index)))
  }

  const handleApplyOptimizations = () => {
    if (acceptedSuggestions.size === 0) {
      showErrorToast(t("toast.selectSuggestionToApply"))
      return
    }

    setIsApplying(true)

    try {
      const optimizedQuestions: string[] = []

      suggestions.forEach((suggestion, index) => {
        if (acceptedSuggestions.has(index) && suggestion.suggested_question) {
          optimizedQuestions.push(suggestion.suggested_question)
        } else {
          optimizedQuestions.push(suggestion.original_question)
        }
      })

      onOptimized(optimizedQuestions)
      showSuccessToast(
        `Applied ${acceptedSuggestions.size} optimization${acceptedSuggestions.size > 1 ? "s" : ""} successfully!`,
      )
      handleClose()
    } catch (error) {
      console.error("Apply optimizations error:", error)
      showErrorToast(t("toast.applyOptimizationsFailed"))
    } finally {
      setIsApplying(false)
    }
  }

  const handleDownloadCsv = async () => {
    if (!checklist || !hasOptimized) return

    setLoadingCsvDownload(true)
    try {
      const csvData = suggestions.map((suggestion, index) => ({
        "Question Number": index + 1,
        "Original Question": suggestion.original_question,
        "Needs Revision": suggestion.needs_revision ? "Yes" : "No",
        "Suggested Revision": suggestion.suggested_question || "N/A",
        "Policy Context": suggestion.policy_context || "N/A",
        "Current Answer": suggestion.current_answer || "N/A",
        Analysis: suggestion.reason,
        Status: acceptedSuggestions.has(index) ? "Accepted" : "Not Applied",
      }))

      const headers = Object.keys(csvData[0])
      const csvContent = [
        headers.join(","),
        ...csvData.map((row) =>
          headers
            .map((header) => `"${String(row[header as keyof typeof row]).replace(/"/g, '""')}"`)
            .join(","),
        ),
      ].join("\n")

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      const url = URL.createObjectURL(blob)
      link.setAttribute("href", url)
      link.setAttribute(
        "download",
        `checklist_optimization_${new Date().toISOString().split("T")[0]}.csv`,
      )
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      showSuccessToast(t("toast.csvFileDownloaded"))
    } catch (error) {
      console.error("CSV download error:", error)
      showErrorToast(t("toast.csvDownloadFailedGeneric"))
    } finally {
      setLoadingCsvDownload(false)
    }
  }

  const toggleAnswerExpansion = (index: number) => {
    const newExpanded = new Set(expandedAnswers)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedAnswers(newExpanded)
  }

  const handleClose = () => {
    // Cancel any ongoing request when closing
    if (ongoingRequestRef.current) {
      ongoingRequestRef.current.cancel()
      ongoingRequestRef.current = null
    }

    setFileItems([])
    setIsLoading(false)
    setSuggestions([])
    setAcceptedSuggestions(new Set())
    setIsApplying(false)
    setSearchMode("vector")
    setCustomInstructions("")
    setLoadingCsvDownload(false)
    setEditingSuggestions(new Map())
    setEditingModes(new Set())
    setHasOptimized(false)
    setExpandedAnswers(new Set())
    onClose()
  }

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && handleClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner style={{ zIndex: 2500 }}>
          <Dialog.Content maxW="6xl" maxH="90vh" display="flex" flexDirection="column">
            <Dialog.Header flexShrink={0}>
              <Dialog.Title>{t("optimizeChecklistModal.title")}</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body
              flex={1}
              overflow={suggestions.length > 0 ? "auto" : "hidden"}
              display="flex"
              flexDirection="column"
            >
              {/* Configuration and Analysis Section */}
              <VStack
                gap={4}
                align="stretch"
                flexShrink={0}
                pb={4}
                borderBottom="1px solid"
                borderColor="gray.200"
              >
                <HStack gap={6} align="flex-start">
                  <VStack flex={1} align="stretch" gap={4}>
                    <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

                    <Field
                      label={t("optimizeChecklistModal.customInstructionsLabel")}
                      helperText={t("optimizeChecklistModal.customInstructionsHelperText")}
                    >
                      <Textarea
                        value={customInstructions}
                        onChange={(e) => setCustomInstructions(e.target.value)}
                        placeholder={t("optimizeChecklistModal.customInstructionsPlaceholder")}
                        rows={2}
                        maxLength={2000}
                      />
                      <Text fontSize="xs" color="gray.500" mt={1}>
                        {customInstructions.length}/2000 characters
                      </Text>
                    </Field>
                  </VStack>

                  <Box flex={1}>
                    <Text mb={2} fontWeight="medium">
                      {t("optimizeChecklistModal.uploadDocumentsTitle")}
                    </Text>
                    <Text fontSize="sm" color="gray.600" mb={2}>
                      {t("optimizeChecklistModal.uploadDocumentsHelperText")}
                    </Text>
                    <FileUpload files={fileItems} onFilesChange={setFileItems} />
                  </Box>
                </HStack>

                <HStack justifyContent="space-between">
                  <Button
                    onClick={handleOptimize}
                    loading={isLoading}
                    colorScheme="blue"
                    disabled={
                      !checklist?.questions ||
                      fileItems.length === 0 ||
                      !fileItems.some((item) => item.file.size > 0)
                    }
                  >
                    {isLoading
                      ? t("optimizeChecklistModal.analyzing")
                      : t("optimizeChecklistModal.analyzeButton")}
                  </Button>

                  {hasOptimized && suggestions.length > 0 && (
                    <HStack gap={2}>
                      <Text fontSize="sm" color="gray.600">
                        {t("optimizeChecklistModal.opportunitiesFound", {
                          count: suggestions.filter((s) => s.needs_revision).length,
                          total: suggestions.length,
                        })}
                      </Text>
                      <Button
                        onClick={handleDownloadCsv}
                        loading={loadingCsvDownload}
                        variant="outline"
                        size="sm"
                      >
                        {loadingCsvDownload
                          ? t("optimizeChecklistModal.downloading")
                          : t("optimizeChecklistModal.downloadCsv")}
                      </Button>
                    </HStack>
                  )}
                </HStack>
              </VStack>

              {/* Loading State */}
              {isLoading && (
                <Box
                  textAlign="center"
                  py={12}
                  flex={1}
                  display="flex"
                  flexDirection="column"
                  justifyContent="center"
                >
                  <Spinner size="lg" />
                  <Text mt={4} color="gray.600">
                    {t("optimizeChecklistModal.analyzingMessage")}
                  </Text>
                  <Button
                    mt={4}
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (ongoingRequestRef.current) {
                        ongoingRequestRef.current.cancel()
                        ongoingRequestRef.current = null
                      }
                      setIsLoading(false)
                      showSuccessToast(t("toast.optimizationCancelled"))
                    }}
                  >
                    {t("optimizeChecklistModal.cancelAnalysis")}
                  </Button>
                </Box>
              )}

              {/* Two-Column Results Layout */}
              {suggestions.length > 0 && !isLoading && (
                <Box flex={1} display="flex" flexDirection="column" pt={4}>
                  <HStack gap={6} flex={1} align="stretch">
                    {/* Left Column: Suggestions that need revision */}
                    <VStack flex={1} align="stretch">
                      <Text fontWeight="semibold" color="blue.700" mb={3}>
                        {t("optimizeChecklistModal.questionsNeedingOptimization")} (
                        {suggestions.filter((s) => s.needs_revision).length})
                      </Text>
                      <Box pr={2}>
                        <VStack gap={4} align="stretch">
                          {suggestions
                            .map((suggestion, index) => ({ suggestion, index }))
                            .filter(({ suggestion }) => suggestion.needs_revision)
                            .map(({ suggestion, index }) => (
                              <Box
                                key={index}
                                p={4}
                                border="1px solid"
                                borderColor="blue.200"
                                borderRadius="md"
                                bg="blue.50"
                              >
                                <VStack align="stretch" gap={3}>
                                  <HStack justifyContent="space-between" align="flex-start">
                                    <Text fontWeight="medium" color="gray.700">
                                      Question {index + 1}
                                    </Text>
                                    <HStack gap={2}>
                                      <IconButton
                                        aria-label="Edit suggestion"
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => handleEditSuggestion(index)}
                                        disabled={editingModes.has(index)}
                                      >
                                        <FiEdit3 />
                                      </IconButton>
                                      <Button
                                        size="sm"
                                        variant={
                                          acceptedSuggestions.has(index) ? "solid" : "outline"
                                        }
                                        colorScheme={
                                          acceptedSuggestions.has(index) ? "green" : "gray"
                                        }
                                        onClick={() => handleSuggestionToggle(index)}
                                      >
                                        {acceptedSuggestions.has(index) ? (
                                          <>
                                            <FiCheck /> {t("optimizeChecklistModal.selected")}
                                          </>
                                        ) : (
                                          t("optimizeChecklistModal.select")
                                        )}
                                      </Button>
                                    </HStack>
                                  </HStack>

                                  <Box>
                                    <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>
                                      {t("optimizeChecklistModal.original")}:
                                    </Text>
                                    <Text
                                      fontSize="sm"
                                      bg="white"
                                      p={2}
                                      borderRadius="md"
                                      border="1px solid"
                                      borderColor="gray.200"
                                    >
                                      {suggestion.original_question}
                                    </Text>
                                  </Box>

                                  <Box>
                                    <Text fontSize="sm" fontWeight="medium" color="blue.600" mb={1}>
                                      {t("optimizeChecklistModal.suggestedImprovement")}:
                                    </Text>
                                    {editingModes.has(index) ? (
                                      <VStack align="stretch" gap={2}>
                                        <Textarea
                                          value={editingSuggestions.get(index) || ""}
                                          onChange={(e) =>
                                            setEditingSuggestions(
                                              new Map(
                                                editingSuggestions.set(index, e.target.value),
                                              ),
                                            )
                                          }
                                          size="sm"
                                          resize="vertical"
                                          minH="80px"
                                        />
                                        <HStack gap={2}>
                                          <Button
                                            size="sm"
                                            colorScheme="green"
                                            onClick={() => handleSaveSuggestion(index)}
                                          >
                                            <FiSave /> Save
                                          </Button>
                                          <Button
                                            size="sm"
                                            variant="ghost"
                                            onClick={() => handleCancelEdit(index)}
                                          >
                                            <FiX /> Cancel
                                          </Button>
                                        </HStack>
                                      </VStack>
                                    ) : (
                                      <Text
                                        fontSize="sm"
                                        bg="white"
                                        p={2}
                                        borderRadius="md"
                                        color="blue.800"
                                        border="1px solid"
                                        borderColor="blue.200"
                                      >
                                        {suggestion.suggested_question}
                                      </Text>
                                    )}
                                  </Box>

                                  {/* Policy Context Section */}
                                  {suggestion.policy_context && (
                                    <Box>
                                      <Text
                                        fontSize="sm"
                                        fontWeight="medium"
                                        color="purple.600"
                                        mb={1}
                                      >
                                        {t("optimizeChecklistModal.policyContext")}:
                                      </Text>
                                      <Text
                                        fontSize="sm"
                                        bg="white"
                                        p={2}
                                        borderRadius="md"
                                        border="1px solid"
                                        borderColor="purple.200"
                                        color="gray.700"
                                        style={{
                                          overflow: expandedAnswers.has(index)
                                            ? "visible"
                                            : "hidden",
                                          display: expandedAnswers.has(index)
                                            ? "block"
                                            : "-webkit-box",
                                          WebkitLineClamp: expandedAnswers.has(index) ? "none" : 2,
                                          WebkitBoxOrient: "vertical" as const,
                                        }}
                                      >
                                        {suggestion.policy_context}
                                      </Text>
                                    </Box>
                                  )}

                                  {/* Current Answer Section */}
                                  <Box>
                                    <Text
                                      fontSize="sm"
                                      fontWeight="medium"
                                      color="orange.600"
                                      mb={1}
                                    >
                                      {t("optimizeChecklistModal.currentAnswer")}:
                                    </Text>
                                    <Text
                                      fontSize="sm"
                                      bg="white"
                                      p={2}
                                      borderRadius="md"
                                      border="1px solid"
                                      borderColor="orange.200"
                                      color="gray.700"
                                      style={{
                                        overflow: expandedAnswers.has(index) ? "visible" : "hidden",
                                        display: expandedAnswers.has(index)
                                          ? "block"
                                          : "-webkit-box",
                                        WebkitLineClamp: expandedAnswers.has(index) ? "none" : 2,
                                        WebkitBoxOrient: "vertical" as const,
                                      }}
                                    >
                                      {suggestion.current_answer}
                                    </Text>
                                  </Box>

                                  <Box>
                                    <HStack justifyContent="space-between" align="center">
                                      <Text fontSize="sm" fontWeight="medium" color="gray.600">
                                        {t("optimizeChecklistModal.analysis")}:
                                      </Text>
                                      <Button
                                        size="xs"
                                        variant="ghost"
                                        onClick={() => toggleAnswerExpansion(index)}
                                      >
                                        {expandedAnswers.has(index)
                                          ? t("optimizeChecklistModal.showLess")
                                          : t("optimizeChecklistModal.showMore")}
                                      </Button>
                                    </HStack>
                                    <Text
                                      fontSize="sm"
                                      color="gray.700"
                                      bg="white"
                                      p={2}
                                      borderRadius="md"
                                      border="1px solid"
                                      borderColor="gray.200"
                                      style={{
                                        overflow: expandedAnswers.has(index) ? "visible" : "hidden",
                                        display: expandedAnswers.has(index)
                                          ? "block"
                                          : "-webkit-box",
                                        WebkitLineClamp: expandedAnswers.has(index) ? "none" : 3,
                                        WebkitBoxOrient: "vertical" as const,
                                      }}
                                    >
                                      {suggestion.reason}
                                    </Text>
                                  </Box>
                                </VStack>
                              </Box>
                            ))}
                        </VStack>
                      </Box>
                    </VStack>

                    {/* Right Column: Questions that are already good */}
                    <VStack flex={1} align="stretch">
                      <Text fontWeight="semibold" color="green.700" mb={3}>
                        {t("optimizeChecklistModal.questionsAlreadyOptimized")} (
                        {suggestions.filter((s) => !s.needs_revision).length})
                      </Text>
                      <Box pr={2}>
                        <VStack gap={4} align="stretch">
                          {suggestions
                            .map((suggestion, index) => ({ suggestion, index }))
                            .filter(({ suggestion }) => !suggestion.needs_revision)
                            .map(({ suggestion, index }) => (
                              <Box
                                key={index}
                                p={4}
                                border="1px solid"
                                borderColor="green.200"
                                borderRadius="md"
                                bg="green.50"
                              >
                                <VStack align="stretch" gap={3}>
                                  <HStack justifyContent="space-between" align="flex-start">
                                    <Text fontWeight="medium" color="gray.700">
                                      Question {index + 1}
                                    </Text>
                                    <Text fontSize="sm" color="green.600" fontWeight="medium">
                                      ✓ Optimized
                                    </Text>
                                  </HStack>

                                  <Box>
                                    <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>
                                      Question:
                                    </Text>
                                    <Text
                                      fontSize="sm"
                                      bg="white"
                                      p={2}
                                      borderRadius="md"
                                      border="1px solid"
                                      borderColor="gray.200"
                                    >
                                      {suggestion.original_question}
                                    </Text>
                                  </Box>

                                  {/* Policy Context Section */}
                                  {suggestion.policy_context && (
                                    <Box>
                                      <Text
                                        fontSize="sm"
                                        fontWeight="medium"
                                        color="purple.600"
                                        mb={1}
                                      >
                                        Policy Context:
                                      </Text>
                                      <Text
                                        fontSize="sm"
                                        bg="white"
                                        p={2}
                                        borderRadius="md"
                                        border="1px solid"
                                        borderColor="purple.200"
                                        color="gray.700"
                                        style={{
                                          overflow: expandedAnswers.has(index)
                                            ? "visible"
                                            : "hidden",
                                          display: expandedAnswers.has(index)
                                            ? "block"
                                            : "-webkit-box",
                                          WebkitLineClamp: expandedAnswers.has(index) ? "none" : 2,
                                          WebkitBoxOrient: "vertical" as const,
                                        }}
                                      >
                                        {suggestion.policy_context}
                                      </Text>
                                    </Box>
                                  )}

                                  {/* Current Answer Section */}
                                  <Box>
                                    <Text
                                      fontSize="sm"
                                      fontWeight="medium"
                                      color="green.600"
                                      mb={1}
                                    >
                                      {t("optimizeChecklistModal.currentAnswer")}:
                                    </Text>
                                    <Text
                                      fontSize="sm"
                                      bg="white"
                                      p={2}
                                      borderRadius="md"
                                      border="1px solid"
                                      borderColor="orange.200"
                                      color="gray.700"
                                      style={{
                                        overflow: expandedAnswers.has(index) ? "visible" : "hidden",
                                        display: expandedAnswers.has(index)
                                          ? "block"
                                          : "-webkit-box",
                                        WebkitLineClamp: expandedAnswers.has(index) ? "none" : 2,
                                        WebkitBoxOrient: "vertical" as const,
                                      }}
                                    >
                                      {suggestion.current_answer}
                                    </Text>
                                  </Box>

                                  <Box>
                                    <HStack justifyContent="space-between" align="center">
                                      <Text fontSize="sm" fontWeight="medium" color="gray.600">
                                        {t("optimizeChecklistModal.analysis")}:
                                      </Text>
                                      <Button
                                        size="xs"
                                        variant="ghost"
                                        onClick={() => toggleAnswerExpansion(index)}
                                      >
                                        {expandedAnswers.has(index)
                                          ? t("optimizeChecklistModal.showLess")
                                          : t("optimizeChecklistModal.showMore")}
                                      </Button>
                                    </HStack>
                                    <Text
                                      fontSize="sm"
                                      color="gray.700"
                                      bg="white"
                                      p={2}
                                      borderRadius="md"
                                      border="1px solid"
                                      borderColor="gray.200"
                                      style={{
                                        overflow: expandedAnswers.has(index) ? "visible" : "hidden",
                                        display: expandedAnswers.has(index)
                                          ? "block"
                                          : "-webkit-box",
                                        WebkitLineClamp: expandedAnswers.has(index) ? "none" : 3,
                                        WebkitBoxOrient: "vertical" as const,
                                      }}
                                    >
                                      {suggestion.reason}
                                    </Text>
                                  </Box>
                                </VStack>
                              </Box>
                            ))}
                        </VStack>
                      </Box>
                    </VStack>
                  </HStack>

                  {/* Apply Optimizations Section */}
                  {acceptedSuggestions.size > 0 && (
                    <Box mt={4} pt={4} borderTop="1px" borderColor="gray.200" flexShrink={0}>
                      <HStack justifyContent="space-between" align="center">
                        <Text fontSize="sm" color="gray.600">
                          {acceptedSuggestions.size}{" "}
                          {t("optimizeChecklistModal.optimizationsSelectedText", {
                            count: acceptedSuggestions.size,
                          })}
                        </Text>
                        <Button
                          onClick={handleApplyOptimizations}
                          loading={isApplying}
                          colorScheme="green"
                          size="lg"
                        >
                          {isApplying
                            ? t("optimizeChecklistModal.applying")
                            : t("optimizeChecklistModal.applySelectedOptimizations")}
                        </Button>
                      </HStack>
                    </Box>
                  )}
                </Box>
              )}
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </Portal>
  )
}

export default OptimizeChecklistModal
