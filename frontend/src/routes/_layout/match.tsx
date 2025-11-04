import { type FormConnectForm, FormconnectService, OpenAPI } from "@/client"
import { request as __request } from "@/client/core/request"
import DownloadButton from "@/components/ui/download-button"
import useCustomToast from "@/hooks/useCustomToast"
import { useFormconnectProgress } from "@/hooks/useFormconnectProgress"
import { useOperationCancellation } from "@/hooks/useOperationCancellation"

import { Box, Button, Container, HStack, Heading, Progress, Text, VStack } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import { FiCheck, FiCopy, FiFileText, FiTrash2 } from "react-icons/fi"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import FileUpload, { type FileItem } from "../../components/Common/FileUpload"
import SearchModeToggle from "../../components/Common/SearchModeToggle"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import FeedbackButtons from "../../components/Feedback/FeedbackButtons"
import FormTemplateTable from "../../components/Match/FormTemplateTable"
import { useResults } from "../../contexts/ResultsContext"
import { copyToClipboard } from "../../utils/copyToClipboard"

const FormConnect = () => {
  const { t, i18n, ready } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { registerOperation } = useOperationCancellation()
  const { matchResult, setMatchResult, matchInputs, setMatchInputs, clearMatchResult } =
    useResults()

  // Initialize form state from persisted inputs or defaults
  const [fileItems, setFileItems] = useState<FileItem[]>(matchInputs?.fileItems || [])
  const [forms, setForms] = useState<FormConnectForm[]>([])
  const [selectedForm, setSelectedForm] = useState<FormConnectForm | null>(
    matchInputs?.selectedForm || null,
  )
  const [formName, setFormName] = useState("")
  const [formDescription, setFormDescription] = useState("")
  const [fields, setFields] = useState(matchInputs?.fields || "")
  const [loading, setLoading] = useState(false)
  const [showFormModal, setShowFormModal] = useState(false)

  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
    matchInputs?.searchMode || "vector",
  )

  // Progress tracking
  const [taskId, setTaskId] = useState<string | null>(null)
  const progress = useFormconnectProgress(taskId)
  const hasHandledCompletionRef = useRef(false)

  // Copy and download states
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  // Handle feedback submission
  const handleFeedbackSubmitted = (type: string) => {
    console.log("Feedback submitted for match result:", type)
    showSuccessToast(t("toast.feedbackMarked", { type }))
  }

  // Handle progress completion
  useEffect(() => {
    if (
      taskId &&
      progress.completed &&
      !hasHandledCompletionRef.current &&
      progress.percentage >= 95
    ) {
      console.log("✅ Match task completed, clearing taskId")
      hasHandledCompletionRef.current = true

      setTimeout(() => {
        setTaskId(null)
        hasHandledCompletionRef.current = false
        setLoading(false)
      }, 1500)
    }

    if (taskId && progress.error) {
      console.log("❌ Match task failed:", progress.error)
      setTaskId(null)
      setLoading(false)
      hasHandledCompletionRef.current = false
      showErrorToast(progress.error)
    }
  }, [taskId, progress.completed, progress.error, progress.percentage])

  // Reset completion handler when taskId changes
  useEffect(() => {
    if (taskId) {
      console.log("🔄 New match task started, resetting completion handler")
      hasHandledCompletionRef.current = false
    }
  }, [taskId])

  // Save input parameters to context whenever they change
  useEffect(() => {
    setMatchInputs({
      fileItems,
      selectedForm,
      fields,
      searchMode,
    })
  }, [fileItems, selectedForm, fields, searchMode, setMatchInputs])

  // Clear inputs and restore from context when clear button is clicked
  const handleClearResults = () => {
    clearMatchResult() // Clears both results and inputs
    // Reset local state to blank
    setFileItems([])
    setSelectedForm(null)
    setFields("")
    setSearchMode("vector")
  }

  // Debug effect to log context state
  useEffect(() => {
    console.log("Match tab - context state:", {
      hasResult: !!matchResult,
      resultsLength: matchResult?.results?.length,
    })
  }, [matchResult])

  // Function to copy results to clipboard
  const handleCopyResults = async () => {
    try {
      await copyToClipboard(matchResult?.results || "")
      setCopySuccess(true)
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)
      showSuccessToast(t("toast.resultsCopied"))
    } catch (err) {
      console.error("Failed to copy results:", err)
      showErrorToast(t("toast.resultsCopyFailed"))
    }
  }

  // Function to download results as DOCX
  const handleDownloadDocx = async () => {
    try {
      setLoadingDownload(true)

      const response = await FormconnectService.generateDocx({
        requestBody: {
          content: matchResult?.results || "",
          language: i18n.language,
        },
      })

      console.log("Received DOCX response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)

      // Handle blob response
      let blob
      if (response instanceof Blob) {
        blob = response
      } else if (response instanceof ArrayBuffer) {
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        blob = new Blob([response as any], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }

      console.log("Blob size:", blob.size)

      if (blob.size === 0) {
        throw new Error("Received empty DOCX file")
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url
      a.download = `FormConnect_Results_${timestamp}.docx`

      console.log("DOCX download filename:", `FormConnect_Results_${timestamp}.docx`)
      console.log("About to trigger DOCX download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("DOCX download triggered successfully")
      showSuccessToast(t("toast.resultsDownloaded"))
    } catch (err: any) {
      console.error("Failed to download results:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(
        t("toast.resultsDownloadFailed", {
          error: err.message || "Unknown error",
        }),
      )
    } finally {
      console.log("DOCX download process completed")
      setLoadingDownload(false)
    }
  }

  // Function to download results as CSV
  const handleDownloadCsv = async () => {
    try {
      setLoadingCsvDownload(true)

      const response = await FormconnectService.generateCsv({
        requestBody: { content: matchResult?.results || "" },
      })

      console.log("Received CSV response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)

      // Handle blob response
      let blob
      if (response instanceof Blob) {
        blob = response
      } else if (response instanceof ArrayBuffer) {
        blob = new Blob([response], { type: "text/csv" })
      } else {
        blob = new Blob([response as any], { type: "text/csv" })
      }

      console.log("Blob size:", blob.size)

      if (blob.size === 0) {
        throw new Error("Received empty CSV file")
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url
      a.download = `FormConnect_Results_${timestamp}.csv`

      console.log("CSV download filename:", `FormConnect_Results_${timestamp}.csv`)
      console.log("About to trigger CSV download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("CSV download triggered successfully")
      showSuccessToast(t("toast.csvDownloaded"))
    } catch (err: any) {
      console.error("Failed to download CSV:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showSuccessToast(`Failed to download CSV: ${err.message || "Unknown error"}`)
    } finally {
      console.log("CSV download process completed")
      setLoadingCsvDownload(false)
    }
  }

  const fetchForms = async () => {
    try {
      const data = await FormconnectService.getForms()
      setForms(data)
    } catch (error) {
      console.error("Error fetching forms:", error)
    }
  }

  useEffect(() => {
    fetchForms()
  }, [])

  const mutation = useMutation({
    mutationFn: async (data: {
      fields: string
      digitized_files: File[]
      handwritten_files: File[]
      search_mode: "vector" | "full_scan"
      form_name?: string
    }) => {
      console.log("🎯 Creating match task for progress tracking...")
      console.log(`Using search mode: ${data.search_mode}`)

      // First, create a FormConnect task to get the task_id for progress tracking
      const taskData: any = await __request(OpenAPI, {
        method: "POST",
        url: "/api/v1/formconnect/process/task",
      })

      const newTaskId = taskData.task_id
      console.log("📋 Generated FormConnect task_id:", newTaskId)
      setTaskId(newTaskId)

      // Prepare files arrays
      const digitizedFiles = data.digitized_files || []
      const handwrittenFiles = data.handwritten_files || []

      // Use the SDK's processForm method with task_id in formData
      // This matches how TwinCheck handles progress tracking
      const promise = FormconnectService.processForm({
        formData: {
          fields: data.fields,
          search_mode: data.search_mode,
          form_name: data.form_name,
          task_id: newTaskId,
          digitized_files: digitizedFiles,
          handwritten_files: handwrittenFiles,
        },
      })

      // Register the operation for automatic cancellation on navigation
      return registerOperation(promise)
    },
    onSuccess: (data: any) => {
      console.log("Match Response data:", data)
      console.log("Match interaction_id:", data.results?.interaction_id)

      // Check if the request was cancelled
      if (data.results?.status === "cancelled") {
        console.log("Match operation was cancelled")
        showErrorToast(t("toast.requestCancelled"))
        return
      }

      const interactionId = data.results?.interaction_id
      console.log("Match interactionId for feedback:", interactionId)

      // Handle both comparison and single file responses
      let results = ""
      if (data.results?.comparison) {
        console.log("Comparison data:", data.results.comparison)
        results = data.results.comparison as string
      } else if (data.results?.message) {
        results = `${data.results.message}\n\n${JSON.stringify(data.results.extracted_data, null, 2)}`
      } else {
        results = JSON.stringify(data.results, null, 2)
      }

      // Store result in global state
      setMatchResult({
        results: results,
        interactionId: interactionId as string,
      })

      showSuccessToast(t("match.matchSuccess"))
    },
    onError: (error: any) => {
      console.log("Mutation unsuccessful!")
      showErrorToast(`Form processing failed: ${error.message}`)
    },
  })

  const handleRun = async () => {
    if (fileItems.length < 1) {
      showErrorToast(t("match.selectDocument"))
      return
    }

    if (!fields.trim()) {
      showErrorToast(t("match.selectDocumentToMatch"))
      return
    }

    // Filter out placeholder files
    const validItems = fileItems.filter((item) => item.file.size > 0)
    const files = validItems.map((item) => item.file)

    const requestData = {
      fields: fields,
      digitized_files: files, // Temporarily use digitized_files until API types are regenerated
      handwritten_files: [], // Empty array for now
      search_mode: searchMode,
      form_name: selectedForm?.name,
    }

    setLoading(true) // Set loading to true
    mutation.mutate(requestData, {
      onSettled: () => {
        setLoading(false) // Set loading to false when the process finishes
      },
    })
  }

  return (
    <Container maxW="container.xl" py={8}>
      {/* Tab description */}
      <Text fontSize="sm" color="gray.500" textAlign="center" mb={4} fontStyle="italic">
        {t("match.subtitle")}
      </Text>

      {/* Progress bar overlay while processing */}
      {(loading || progress.isActive || (taskId && !progress.completed)) && (
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="blackAlpha.800"
          zIndex="50"
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
          p={6}
        >
          <VStack gap={4} width="80%" maxWidth="400px">
            <Text color="white" fontSize="lg" fontWeight="medium" textAlign="center">
              {progress.message || t("match.processing")}
            </Text>
            <Box width="100%">
              <Progress.Root value={progress.percentage} size="lg" colorPalette="blue">
                <Progress.Track>
                  <Progress.Range />
                </Progress.Track>
              </Progress.Root>
              <Text color="white" fontSize="sm" textAlign="center" mt={2}>
                {Math.round(progress.percentage)}%
              </Text>
            </Box>
            <Text color="gray.300" fontSize="sm" textAlign="center">
              {ready ? t("match.pleaseWait") : "Please wait while we process your documents"}
            </Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title={t("match.sourceDocument")}
              description={selectedForm ? selectedForm.name : t("match.pleaseSelect")}
              icon={<FiFileText size={24} />}
              isSelected={!!selectedForm}
              onClick={() => setShowFormModal(true)}
              helpKey="formTemplate"
            />

            <FileUpload files={fileItems} onFilesChange={setFileItems} helpKey="fileUpload" />

            <SearchModeToggle
              searchMode={searchMode}
              onSearchModeChange={setSearchMode}
              helpKey="searchMode"
            />
          </VStack>
        </HStack>

        <SelectionModal
          isOpen={showFormModal}
          onClose={() => setShowFormModal(false)}
          title={t("match.selectFormTemplateTitle")}
        >
          <FormTemplateTable
            forms={forms}
            selectedForm={selectedForm}
            onFormChange={setSelectedForm}
            onFieldsChange={setFields}
            onFormsUpdate={fetchForms}
            fields={fields}
            formName={formName}
            setFormName={setFormName}
            formDescription={formDescription}
            setFormDescription={setFormDescription}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={!selectedForm && !matchResult ? 0.3 : 1}
          pointerEvents={!selectedForm && !matchResult ? "none" : "auto"}
        >
          <HStack gap={4} justify="center">
            <Button
              variant="solid"
              onClick={fileItems.length > 0 ? handleRun : handleRun}
              disabled={
                fileItems.length < 1 ||
                !fields.trim() ||
                !fileItems.some((item) => item.file.size > 0)
              }
              loading={loading}
              color="white"
              bg="rgba(0, 65, 72, 0.9)"
              width="20%"
              _hover={{
                bg: "rgba(0, 65, 72, 0.85)",
              }}
            >
              {t("match.findMatches")}
            </Button>
          </HStack>

          <Box
            border="1px solid"
            borderColor="gray.200"
            borderRadius="md"
            p={4}
            mt={4}
            display="flex"
            flexDirection={{ base: "column", md: "row" }}
            gap={4}
          >
            <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
              <Heading size="md" mb={4}>
                {t("ui.results")}
              </Heading>

              <Box
                border="1px solid"
                borderColor="gray.200"
                borderRadius="md"
                p={4}
                bg="surface"
                minH="100px"
                maxH={{ base: "400px", md: "600px" }}
                overflowY="auto"
                position="relative"
              >
                {matchResult ? (
                  <>
                    {/* Copy and Download buttons */}
                    <HStack gap={2} mb={4} justifyContent="flex-end">
                      <Button
                        size="sm"
                        onClick={handleCopyResults}
                        variant="outline"
                        colorScheme={copySuccess ? "green" : "gray"}
                      >
                        {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                        {copySuccess ? t("ui.copied") : t("ui.copyText")}
                      </Button>

                      <DownloadButton
                        size="sm"
                        onClick={handleDownloadDocx}
                        loading={loadingDownload}
                      >
                        {t("ui.downloadDocx")}
                      </DownloadButton>

                      <DownloadButton
                        size="sm"
                        onClick={handleDownloadCsv}
                        loading={loadingCsvDownload}
                      >
                        {t("ui.downloadCsv")}
                      </DownloadButton>

                      <Button
                        size="sm"
                        variant="outline"
                        colorPalette="red"
                        onClick={() => {
                          handleClearResults()
                          showSuccessToast(t("ui.clearResults"))
                        }}
                      >
                        <FiTrash2 />
                        {t("ui.clearResults")}
                      </Button>
                    </HStack>

                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{matchResult.results}</ReactMarkdown>

                    {/* Add feedback buttons for the match result */}
                    {matchResult.interactionId && (
                      <Box
                        position="sticky"
                        bottom={4}
                        right={4}
                        display="flex"
                        justifyContent="flex-end"
                        pointerEvents="auto"
                        zIndex={10}
                        mt={4}
                      >
                        <FeedbackButtons
                          interactionId={matchResult.interactionId}
                          onFeedbackSubmitted={handleFeedbackSubmitted}
                        />
                      </Box>
                    )}
                  </>
                ) : (
                  <Text color="gray.500">{t("match.selectDocumentToMatch")}</Text>
                )}
              </Box>
            </Box>
          </Box>
        </VStack>
      </VStack>
    </Container>
  )
}

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/match")({
  component: FormConnect,
})
