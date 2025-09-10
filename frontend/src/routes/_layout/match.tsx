import {
  type FormConnectForm,
  FormconnectService,
  type KnowledgeBasePublic,
  KnowledgeBasesService,
} from "@/client"
import DownloadButton from "@/components/ui/download-button"
import useCustomToast from "@/hooks/useCustomToast"
import { Box, Button, Container, HStack, Heading, Spinner, Text, VStack } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { FiCheck, FiCopy, FiFileText, FiTrash2 } from "react-icons/fi"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { useTranslation } from "react-i18next"
import FileUpload, { type FileItem } from "../../components/Common/FileUpload"
import SearchModeToggle from "../../components/Common/SearchModeToggle"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import FeedbackButtons from "../../components/Feedback/FeedbackButtons"
import FormTemplateTable from "../../components/Match/FormTemplateTable"
import { useResults } from "../../contexts/ResultsContext"
import { copyToClipboard } from "../../utils/copyToClipboard"

const FormConnect = () => {
  const { t } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()
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
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
    matchInputs?.searchMode || "vector",
  )

  // Copy and download states
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  // Handle feedback submission
  const handleFeedbackSubmitted = (type: string) => {
    console.log("Feedback submitted for match result:", type)
    showSuccessToast(`Thank you for marking this response as ${type}!`)
  }

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
      showSuccessToast("Results copied to clipboard")
    } catch (err) {
      console.error("Failed to copy results:", err)
      showSuccessToast("Failed to copy results to clipboard")
    }
  }

  // Function to download results as DOCX
  const handleDownloadDocx = async () => {
    try {
      setLoadingDownload(true)

      const response = await FormconnectService.generateDocx({
        requestBody: { content: matchResult?.results || "" },
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
      showSuccessToast("Results downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download results:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showSuccessToast(`Failed to download results: ${err.message || "Unknown error"}`)
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
      showSuccessToast("CSV downloaded successfully")
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

  const fetchKnowledgeBases = async () => {
    try {
      const data = await KnowledgeBasesService.readKnowledgeBases()
      setKnowledgeBases(data.data || [])
    } catch (error) {
      console.error("Error fetching knowledge bases:", error)
      setKnowledgeBases([])
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
    fetchKnowledgeBases()
  }, [])

  const mutation = useMutation({
    mutationFn: (data: {
      fields: string
      digitized_files: File[]
      handwritten_files: File[]
      search_mode: "vector" | "full_scan"
    }) => {
      console.log("Now beginning mutation...")
      console.log(`Using search mode: ${data.search_mode}`)

      return FormconnectService.processForm({
        fields: data.fields,
        searchMode: data.search_mode,
        formData: {
          digitized_files: data.digitized_files,
          handwritten_files: data.handwritten_files,
        },
      })
    },
    onSuccess: (data) => {
      console.log("Match Response data:", data)
      console.log("Match interaction_id:", data.results.interaction_id)

      const interactionId = data.results.interaction_id
      console.log("Match interactionId for feedback:", interactionId)

      // Handle both comparison and single file responses
      let results = ""
      if (data.results.comparison) {
        console.log("Comparison data:", data.results.comparison)
        results = data.results.comparison as string
      } else if (data.results.message) {
        results = `${data.results.message}\n\n${JSON.stringify(data.results.extracted_data, null, 2)}`
      } else {
        results = JSON.stringify(data.results, null, 2)
      }

      // Store result in global state
      setMatchResult({
        results: results,
        interactionId: interactionId as string,
      })

      const searchMethod = searchMode === "vector" ? "vector search" : "full document scan"
      showSuccessToast(`Form processing completed using ${searchMethod}!`)
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

    // Filter out placeholder files and separate into digitized vs handwritten
    const validItems = fileItems.filter((item) => item.file.size > 0)
    const digitizedFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)
    const handwrittenFiles = validItems
      .filter((item) => item.isHandwritten)
      .map((item) => item.file)

    const requestData = {
      fields: fields,
      digitized_files: digitizedFiles,
      handwritten_files: handwrittenFiles,
      search_mode: searchMode,
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

            <FileUpload
              files={fileItems}
              onFilesChange={setFileItems}
              showHandwrittenToggle={true}
              helpKey="fileUpload"
            />

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
            knowledgeBases={knowledgeBases}
            searchMode={searchMode}
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
                Results
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
                opacity={loading ? 0.5 : 1}
              >
                {loading && (
                  <Box
                    position="absolute"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    zIndex="1"
                  >
                    <Spinner size="lg" color="blue.500" />
                  </Box>
                )}
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
                        {copySuccess ? "Copied!" : "Copy Text"}
                      </Button>

                      <DownloadButton
                        size="sm"
                        onClick={handleDownloadDocx}
                        loading={loadingDownload}
                      >
                        Download DOCX
                      </DownloadButton>

                      <DownloadButton
                        size="sm"
                        onClick={handleDownloadCsv}
                        loading={loadingCsvDownload}
                      >
                        Download CSV
                      </DownloadButton>

                      <Button
                        size="sm"
                        variant="outline"
                        colorPalette="red"
                        onClick={() => {
                          handleClearResults()
                          showSuccessToast("Match results cleared")
                        }}
                      >
                        <FiTrash2 />
                        Clear Results
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
