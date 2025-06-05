import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Switch,
  Field as ChakraField,
  Spinner,
  Separator,
  Accordion,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import { CancelablePromise } from "@/client/core/CancelablePromise"
import SourceLink from "@/components/Common/SourceLink"
import FileUpload, { FileItem } from "@/components/Common/FileUpload"
import { useState, useEffect, useRef } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import {
  VeradocService,
  KnowledgeBasesService,
  KnowledgeBasePublic,
  VeraDocChecklist,
} from "@/client"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FiFileText, FiDatabase, FiCopy, FiCheck, FiDownload } from "react-icons/fi"
import { Field } from "../../components/ui/field"
import KnowledgeBaseTable from "../../components/Review/KnowledgeBaseTable"
import ChecklistTable from "../../components/Review/ChecklistTable"
import SelectionCard from "../../components/Review/SelectionCard"
import SelectionModal from "../../components/Review/SelectionModal"

const VeraDoc = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])
  const abortControllerRef = useRef<AbortController | null>(null)
  const ongoingRequest = useRef<CancelablePromise<any> | null>(null)

  // Add modal state for knowledge base and checklist selection
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [showChecklistModal, setShowChecklistModal] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)

  const [questions, setQuestions] = useState("")

  // File management state - using the new FileItem interface
  const [fileItems, setFileItems] = useState<FileItem[]>([])
  const [mode, setMode] = useState<"manual" | "batch">("manual")

  // Batch processing state
  const [batchResults, setBatchResults] = useState<
    Array<{ displayResults: string; qaPairs: any[] }>
  >([])
  const [selectedBatchResult, setSelectedBatchResult] = useState<number>(0)
  const [batchLoading, setBatchLoading] = useState<boolean>(false)

  const [qaPairs, setQaPairs] = useState<Array<any>>([])
  const [checklists, setChecklists] = useState<VeraDocChecklist[]>([])
  const [selectedChecklist, setSelectedChecklist] = useState<VeraDocChecklist | null>(null)
  const [checklistName, setChecklistName] = useState("")
  const [checklistDescription, setChecklistDescription] = useState("")

  const [results, setResults] = useState("")
  const [loading, setLoading] = useState(false)

  const handleCopyReport = async () => {
    try {
      // Prepare combined text with evaluation summary and QA pairs
      let fullText = `# Evaluation Summary\n\n${results}\n\n# Question-Answer Details\n\n`

      // Add each question and its answer
      qaPairs.forEach((pair, index) => {
        fullText += `## Question ${index + 1}: ${pair.question}\n\n`
        fullText += `### Answer\n${pair.answer}\n\n`
        fullText += `### Relevant Policy Context\n${pair.context}\n\n`
      })

      await navigator.clipboard.writeText(fullText)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast("Report copied to clipboard")
    } catch (err) {
      console.error("Failed to copy report:", err)
      showErrorToast("Failed to copy report to clipboard")
    }
  }

  const handleDownloadReport = async () => {
    try {
      setLoadingDownload(true)

      // Prepare combined text with evaluation summary and QA pairs
      let fullText = `# Evaluation Summary\n\n${results}\n\n# Question-Answer Details\n\n`

      // Add each question and its answer
      qaPairs.forEach((pair, index) => {
        fullText += `## Question ${index + 1}: ${pair.question}\n\n`
        fullText += `### Answer\n${pair.answer}\n\n`
        fullText += `### Relevant Policy Context\n${pair.context}\n\n`
      })

      const response = await VeradocService.generateDocx({
        requestBody: { content: fullText },
      })

      let blob
      if (response instanceof Blob) {
        console.log("Response is a Blob")
        blob = response
      } else if (response instanceof ArrayBuffer) {
        console.log("Response is an ArrayBuffer")
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        console.log("Response is a string or unexpected type")
        blob = new Blob([response as any], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url
      a.download = `evaluation_${timestamp}.docx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast("Evaluation downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download report:", err)
      showErrorToast(`Failed to download evaluation: ${err.message || "Unknown error"}`)
    } finally {
      setLoadingDownload(false)
    }
  }

  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown"

    // Clean up temporary file paths
    if (source.includes("/tmp/") || source.includes("\\tmp\\")) {
      // First get the filename without the path
      const filename = source.split("/").pop() || source.split("\\").pop() || ""

      // Then remove everything before and including the first underscore
      return filename.includes("_") ? filename.substring(filename.indexOf("_") + 1) : filename
    }

    return source
  }

  // Add this effect to fetch knowledge bases when component mounts
  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        // Assuming your service has a method to fetch knowledge bases
        const response = await KnowledgeBasesService.readKnowledgeBases({
          skip: 0,
          limit: 100, // Get all knowledge bases
        })
        setKnowledgeBases(response.data || [])
      } catch (error) {
        console.error("Error fetching knowledge bases:", error)
      }
    }

    fetchKnowledgeBases()
  }, [])

  // Add these state variables with your other state definitions
  const [selectedKnowledgeBaseDetails, setSelectedKnowledgeBaseDetails] = useState<any>(null)

  // Add this function to fetch knowledge base details including sources
  const fetchKnowledgeBaseDetails = async (knowledgeBaseId: string) => {
    try {
      const response = await KnowledgeBasesService.readKnowledgeBase({ id: knowledgeBaseId })
      setSelectedKnowledgeBaseDetails(response)
    } catch (error) {
      console.error("Error fetching knowledge base details:", error)
      showErrorToast("Failed to fetch knowledge base details")
    }
  }

  const fetchChecklists = async () => {
    try {
      const data = await VeradocService.getChecklists()
      setChecklists(data)
    } catch (error) {
      console.error("Error fetching checklists:", error)
    }
  }

  useEffect(() => {
    fetchChecklists()
  }, [])

  // Add this mutation hook inside your VeraDoc component, before your handleRun function
  const mutation = useMutation({
    mutationFn: (data: {
      questions: string
      knowledgeBaseId: string
      files: File[]
      handwrittenFiles: File[]
    }) => {
      if (ongoingRequest.current) {
        ongoingRequest.current.cancel()
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }

      // Create a new controller and store directly in the ref
      const controller = new AbortController()
      abortControllerRef.current = controller

      console.log("Creating new request with fresh AbortController")

      // Create the promise and store it
      const promise = VeradocService.processRagChecklist({
        questions: data.questions,
        knowledgeBaseId: data.knowledgeBaseId,
        formData: {
          files: data.files,
          handwritten_files: data.handwrittenFiles,
        },
      })

      ongoingRequest.current = promise
      return promise
    },
    onSuccess: (data: any) => {
      console.log("Response data:", data)

      setResults(data.results.final_evaluation)

      // Store the QA pairs to render with custom components
      setQaPairs(data.results.qa_pairs || [])
    },
    onError: (error) => {
      console.log("RAG mutation unsuccessful!")
      setResults(`Error: ${error.message}`)
    },
    onSettled: () => {
      ongoingRequest.current = null
      setLoading(false)
    },
  })

  const handleRun = async () => {
    if (fileItems.length < 1) {
      setResults("Please upload at least one file.")
      return
    }

    if (!questions.trim()) {
      setResults("Please enter at least one question.")
      return
    }

    if (!selectedKnowledgeBase) {
      setResults("Please select a knowledge base for context.")
      return
    }

    // Filter out placeholder files and separate into regular vs handwritten
    const validItems = fileItems.filter((item) => item.file.size > 0)
    const regularFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)
    const handwrittenFiles = validItems
      .filter((item) => item.isHandwritten)
      .map((item) => item.file)

    if (validItems.length < 1) {
      setResults("Please upload at least one valid file.")
      return
    }

    const requestData = {
      questions: questions,
      knowledgeBaseId: selectedKnowledgeBase.id,
      files: regularFiles,
      handwrittenFiles: handwrittenFiles,
    }

    console.log("Request Data:", requestData)

    setLoading(true) // Set loading to true
    mutation.mutate(requestData, {
      onSettled: () => {
        setLoading(false) // Set loading to false when the process finishes
      },
    })
  }

  const handleProcessBatch = async () => {
    if (fileItems.length === 0) {
      setResults("Error: Please upload at least one file for batch processing.")
      return
    }

    if (!questions.trim()) {
      setResults("Error: Please enter at least one question.")
      return
    }

    if (!selectedKnowledgeBase) {
      setResults("Error: Please select a knowledge base for context.")
      return
    }

    // Clear previous results
    setBatchResults([])
    setSelectedBatchResult(0)
    setBatchLoading(true)

    // Cancel any ongoing requests
    if (ongoingRequest.current) {
      ongoingRequest.current.cancel()
    }

    // Cancel any in-flight fetch requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create a new controller and store directly in the ref
    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      const results: Array<{ displayResults: string; qaPairs: any[] }> = []

      // Process each file individually
      for (let i = 0; i < fileItems.length; i++) {
        if (controller.signal.aborted) {
          console.log("Batch processing aborted")
          break
        }
        const fileItem = fileItems[i]

        // Separate files based on handwritten flag
        const regularFiles = fileItem.isHandwritten ? [] : [fileItem.file]
        const handwrittenFiles = fileItem.isHandwritten ? [fileItem.file] : []

        // Process this file
        const requestData = {
          questions: questions,
          knowledgeBaseId: selectedKnowledgeBase.id,
          files: regularFiles,
          handwrittenFiles: handwrittenFiles,
        }

        // Call the API using our mutation
        const response = await VeradocService.processRagChecklist({
          questions: requestData.questions,
          knowledgeBaseId: requestData.knowledgeBaseId,
          formData: {
            files: requestData.files,
            handwritten_files: requestData.handwrittenFiles,
          },
        })

        // Format the response
        let displayResults = `# Analysis Results for ${fileItem.file.name}\n\n`

        if (response.results.final_evaluation) {
          displayResults += "## FINAL EVALUATION\n\n"
          displayResults += response.results.final_evaluation + "\n\n"
        }

        // Store the QA pairs in the results array
        results.push({
          displayResults,
          qaPairs: response.results.qa_pairs || [],
        })

        // Update your state for batch results
        setBatchResults(results)
      }
    } catch (error: any) {
      // Handle errors, checking if it's an abort
      if (error.name === "AbortError") {
        console.log("Batch processing was aborted")
      } else {
        console.error("Batch processing error:", error)
        setResults(`Error processing batch: ${error.message}`)
      }
    } finally {
      setBatchLoading(false)
    }
  }

  // Create custom components for table rendering
  const components = {
    table: (props: any) => (
      <Box
        as="table"
        width="full"
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        {...props}
      />
    ),
    thead: (props: any) => <Box as="thead" bg="gray.100" {...props} />,
    tbody: (props: any) => <Box as="tbody" {...props} />,
    tr: (props: any) => <Box as="tr" {...props} />,
    th: (props: any) => (
      <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
    ),
    td: (props: any) => <Box as="td" p={4} borderBottomWidth="1px" {...props} />,
  }

  return (
    <Container maxW="container.xl" py={8}>
      {/* Add this overlay spinner that shows when batchLoading is true */}
      {batchLoading && (
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="rgba(255, 255, 255, 0.7)"
          zIndex="10"
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
        >
          <VStack gap={4}>
            <Spinner size="xl" color="blue.500" />
            <Text fontWeight="medium">Processing batch files...</Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title="Knowledge Base"
              description={
                selectedKnowledgeBase ? `${selectedKnowledgeBase.title}` : "Click to select"
              }
              icon={<FiDatabase size={24} />}
              isSelected={!!selectedKnowledgeBase}
              onClick={() => setShowKnowledgeBaseModal(true)}
            />

            <SelectionCard
              title="Checklist"
              description={selectedChecklist ? selectedChecklist.name : "Click to select"}
              icon={<FiFileText size={24} />}
              isSelected={!!selectedChecklist}
              isDisabled={!selectedKnowledgeBase}
              onClick={() => selectedKnowledgeBase && setShowChecklistModal(true)}
            />

            {/* File Upload Component */}
            <FileUpload
              files={fileItems}
              onFilesChange={setFileItems}
              showHandwrittenToggle={true}
            />
          </VStack>
        </HStack>

        <SelectionModal
          isOpen={showKnowledgeBaseModal}
          onClose={() => setShowKnowledgeBaseModal(false)}
          title="Select Knowledge Base"
        >
          <KnowledgeBaseTable
            knowledgeBases={knowledgeBases}
            selectedKnowledgeBase={selectedKnowledgeBase}
            onSelectionChange={setSelectedKnowledgeBase}
          />
        </SelectionModal>

        <SelectionModal
          isOpen={showChecklistModal}
          onClose={() => setShowChecklistModal(false)}
          title="Select Checklist"
        >
          <ChecklistTable
            checklists={checklists}
            selectedChecklist={selectedChecklist}
            onChecklistChange={setSelectedChecklist}
            onQuestionsChange={setQuestions}
            onChecklistsUpdate={fetchChecklists}
            questions={questions}
            isDisabled={!selectedKnowledgeBase}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={!selectedKnowledgeBase || !selectedChecklist ? 0.3 : 1}
          pointerEvents={!selectedKnowledgeBase || !selectedChecklist ? "none" : "auto"}
        >
          {/* Mode Toggle */}
          {/* <Field>
            <HStack justify="space-between" align="center">
              <Text fontWeight="medium">Mode:</Text>
              <HStack align="center">
                <Text>Manual</Text>
                <Switch.Root id="mode-toggle" colorPalette="teal">
                  <Switch.HiddenInput
                    checked={mode === "batch"}
                    onChange={(e) => setMode(e.target.checked ? "batch" : "manual")}
                  />
                  <Switch.Control>
                    <Switch.Thumb />
                  </Switch.Control>
                </Switch.Root>
                <Text>Batch</Text>
              </HStack>
            </HStack>
          </Field> */}

          <HStack gap={4}>
            <Button
              variant="solid"
              onClick={fileItems.length > 0 ? handleProcessBatch : handleRun}
              disabled={
                fileItems.length < 1 ||
                !questions.trim() ||
                !fileItems.some((item) => item.file.size > 0)
              }
              loading={loading || batchLoading}
            >
              Run
            </Button>
          </HStack>

          <Separator my={4} />

          {/* Results Panel */}
          <Box display="flex" flexDirection={{ base: "column", md: "row" }} gap={4}>
            {/* Results Panel - Always take remaining space */}
            <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
              {/* Title for Results */}
              <HStack justify="space-between" align="center" mb={4}>
                <Heading size="md">
                  {mode === "batch" ? "Batch Processing Results" : "Results"}
                </Heading>

                {/* Add Copy and Download buttons */}
                {results && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyReport}
                      colorPalette={copySuccess ? "green" : "blue"}
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess ? "Copied!" : "Copy Text"}
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleDownloadReport}
                      loading={loadingDownload}
                      colorPalette="green"
                    >
                      <FiDownload />
                      Download DOCX
                    </Button>
                  </HStack>
                )}
              </HStack>

              {/* Results Box - This is the main content area */}
              <Box
                border="1px solid"
                borderColor="gray.200"
                borderRadius="md"
                p={4}
                bg="gray.50"
                minH="100px"
                maxH={{ base: "400px", md: "600px" }}
                overflowY="auto"
                position="relative"
                opacity={loading || batchLoading ? 0.5 : 1}
              >
                {(loading || batchLoading) && (
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
                {results ? (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {results}
                    </ReactMarkdown>

                    {qaPairs.length > 0 && (
                      <Box mt={4}>
                        {qaPairs.map((pair, index) => (
                          <Box
                            key={index}
                            mb={4}
                            p={4}
                            borderWidth="1px"
                            borderRadius="md"
                            bg="white"
                          >
                            <Heading as="h3" size="md" mb={2}>
                              Question {index + 1}: {pair.question}
                            </Heading>

                            <Box mb={3}>
                              <Text fontWeight="bold">Answer:</Text>
                              <Text>{pair.answer}</Text>
                            </Box>

                            <Box mb={3}>
                              <Text fontWeight="bold">Relevant Policy Context:</Text>
                              <Text>{pair.context}</Text>
                            </Box>

                            {pair.source_citations && pair.source_citations.length > 0 && (
                              <Accordion.Root multiple>
                                <Accordion.Item value={`citations-${index}`}>
                                  <h2>
                                    <Accordion.ItemTrigger
                                      bg="gray.100"
                                      _hover={{ bg: "gray.200" }}
                                    >
                                      <Box flex="1" textAlign="left" fontWeight="medium">
                                        <HStack>
                                          <FiFileText />
                                          <Text>
                                            View Source Citations ({pair.source_citations.length})
                                          </Text>
                                        </HStack>
                                      </Box>
                                    </Accordion.ItemTrigger>
                                  </h2>
                                  <Accordion.ItemContent pb={4} bg="gray.50">
                                    {pair.source_citations.map((citation: any, cIndex: number) => (
                                      <Box
                                        key={cIndex}
                                        p={3}
                                        mb={2}
                                        borderWidth="1px"
                                        borderRadius="md"
                                        bg="white"
                                      >
                                        {citation.metadata.source_data_id ? (
                                          <SourceLink
                                            sourceId={citation.metadata.source_data_id}
                                            fileName={getDisplayFileName(citation.metadata.source)}
                                            ml={1}
                                            fontWeight="normal"
                                            color="blue.600"
                                            useModal={true}
                                          />
                                        ) : (
                                          <Text
                                            as="span"
                                            ml={1}
                                            fontWeight="normal"
                                            color="blue.600"
                                          >
                                            {getDisplayFileName(citation.metadata.source)}
                                          </Text>
                                        )}
                                        <Box
                                          mt={2}
                                          p={2}
                                          bg="gray.50"
                                          borderRadius="sm"
                                          fontSize="sm"
                                          whiteSpace="pre-wrap"
                                        >
                                          {citation.content}
                                        </Box>
                                      </Box>
                                    ))}
                                  </Accordion.ItemContent>
                                </Accordion.Item>
                              </Accordion.Root>
                            )}
                          </Box>
                        ))}
                      </Box>
                    )}
                  </>
                ) : (
                  <Text color="gray.500">Results will appear here after running.</Text>
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
export const Route = createFileRoute("/_layout/veradoc")({
  component: VeraDoc,
})
