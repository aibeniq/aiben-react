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
  Input,
  Separator,
  Accordion,
  Card,
  IconButton,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import { CancelablePromise } from "@/client/core/CancelablePromise"
import SourceLink from "@/components/Common/SourceLink"
import { useState, useEffect, useRef } from "react"
import { useDropzone } from "react-dropzone"
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
import {
  FiFileText,
  FiDatabase,
  FiTrash2,
  FiChevronUp,
  FiChevronDown,
  FiCopy,
  FiCheck,
  FiDownload,
} from "react-icons/fi"
import { Field } from "../../components/ui/field"
import { format } from "date-fns"
import { useQuery } from "@tanstack/react-query"
import FeedbackButtons from "@/components/Feedback/FeedbackButtons"
import { InteractiveList } from "@/components/ui/interactive-list"
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

  const [reportHistory, setReportHistory] = useState<any[]>([])
  const [selectedHistoryReport, setSelectedHistoryReport] = useState(null)
  const [isHistoryLoading, setIsHistoryLoading] = useState(false)

  const historyQuery = useQuery({
    queryKey: ["veradocHistory"],
    queryFn: async () => {
      const response = await VeradocService.getVeradocHistory({ limit: 20 })
      return response
    },
    enabled: true,
  })

  useEffect(() => {
    if (historyQuery.data) {
      setReportHistory(Array.isArray(historyQuery.data) ? historyQuery.data : [])
    }
    setIsHistoryLoading(historyQuery.isLoading)
  }, [historyQuery.data, historyQuery.isLoading])


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

      // Create a unique document name
      const documentName = selectedHistoryReport?.document_name || "Document"
      const docTitle = `Evaluation of ${documentName}`

      const response = await VeradocService.generateDocx({
        requestBody: { content: fullText, title: docTitle },
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
        blob = new Blob([response], {
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
    } catch (err) {
      console.error("Failed to download report:", err)
      showErrorToast(`Failed to download evaluation: ${err.message || "Unknown error"}`)
    } finally {
      setLoadingDownload(false)
    }
  }

  // Add this function to load a report from history
  const loadReportFromHistory = async (reportId) => {
    try {
      setIsHistoryLoading(true)
      const report = await VeradocService.getVeradocDetail({ reportId })

      // Update UI state with the loaded report
      setResults(report.results.final_evaluation || "")
      setQaPairs(report.results.qa_pairs || [])
      setSelectedHistoryReport(report)

      // If KB ID exists, update the selected knowledge base
      if (report.kb_id) {
        const kb = knowledgeBases.find((kb) => kb.id === report.kb_id)
        if (kb) {
          setSelectedKnowledgeBase(kb)
          fetchKnowledgeBaseDetails(kb.id)
        }
      }

      // Update questions if they exist
      if (report.questions) {
        setQuestions(report.questions)
      }

      showSuccessToast("Evaluation loaded successfully")
    } catch (error) {
      console.error("Error loading report:", error)
      showErrorToast("Failed to load evaluation")
    } finally {
      setIsHistoryLoading(false)
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

  const [mode, setMode] = useState<"manual" | "batch">("manual")

  const [batchFiles, setBatchFiles] = useState<
    Array<{
      file: File
      isHandwritten: boolean
    }>
  >([])

  const [batchResults, setBatchResults] = useState<
    Array<{ displayResults: string; qaPairs: any[] }>
  >([])
  const [selectedBatchResult, setSelectedBatchResult] = useState<number>(0)
  const [batchLoading, setBatchLoading] = useState<boolean>(false)

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        // Convert the new files to our file item format
        const newFileItems = acceptedFiles.map((file) => ({
          file,
          isHandwritten: false,
        }))

        // Add to existing files
        setBatchFiles((prev) => [...prev, ...newFileItems])
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    multiple: true,
  })

  // Add batch uploader
  const addBatchUploader = () => {
    setBatchFileItems((prev) => [...prev, { files: [], isHandwritten: false }])
  }

  // Toggle handwritten status for all files in a batch uploader
  const toggleBatchHandwritten = (index: number) => {
    setBatchFileItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, isHandwritten: !item.isHandwritten } : item)),
    )
  }

  const removeBatchUploader = (index: number) => {
    setBatchFileItems((prev) => prev.filter((_, i) => i !== index))
  }

  const addFilesToBatchUploader = (index: number, newFiles: File[]) => {
    setBatchFileItems((prev) =>
      prev.map((item, i) =>
        i === index
          ? {
              ...item,
              files: [...item.files, ...newFiles],
              isHandwritten: item.isHandwritten, // Preserve the handwritten state
            }
          : item,
      ),
    )
  }

  const getBatchSetCount = () => {
    // Find the minimum number of files across all batch uploaders
    // This represents how many complete sets we can process
    if (!batchFileItems || batchFileItems.length === 0) return 0

    // Get the number of files in each uploader
    const fileCounts = batchFileItems.map((item) => item.files.length)

    // Return the minimum (as we can only process as many complete sets as the column with fewest files)
    return Math.min(...fileCounts)
  }

  const [fileItems, setFileItems] = useState<
    Array<{
      file: File
      isHandwritten: boolean
    }>
  >([])

  const [qaPairs, setQaPairs] = useState<Array<any>>([])
  const [checklists, setChecklists] = useState<VeraDocChecklist[]>([]) // List of checklists
  const [selectedChecklist, setSelectedChecklist] = useState<VeraDocChecklist | null>(null) // Currently selected checklist
  const [checklistName, setChecklistName] = useState("") // Name of the checklist being created/edited
  const [checklistDescription, setChecklistDescription] = useState("") // Description of the checklist

  const [results, setResults] = useState("")
  const [loading, setLoading] = useState(false)

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
      const promise = VeradocService.processRagChecklist(
        {
          questions: data.questions,
          knowledgeBaseId: data.knowledgeBaseId,
          formData: {
            files: data.files,
            handwritten_files: data.handwrittenFiles,
          },
        },
        { signal: controller.signal },
      )

      ongoingRequest.current = promise
      return promise
    },
    onSuccess: (data) => {
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

  const addFile = (file: File) => {
    setFileItems((prevItems) => [...prevItems, { file, isHandwritten: false }])
  }

  const removeFile = (index: number) => {
    setFileItems((prevItems) => prevItems.filter((_, i) => i !== index))
  }

  const updateFile = (index: number, file: File) => {
    setFileItems((prevItems) =>
      prevItems.map((item, i) => (i === index ? { ...item, file } : item)),
    )
  }

  const toggleHandwritten = (index: number) => {
    setFileItems((prevItems) =>
      prevItems.map((item, i) =>
        i === index ? { ...item, isHandwritten: !item.isHandwritten } : item,
      ),
    )
  }

  const handleAddNewFile = () => {
    // This will add a placeholder that will be replaced when the user selects a file
    addFile(new File([], "placeholder"))
  }

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

  // Update your isBatchConfigValid function
  const isBatchConfigValid = () => {
    if (batchFileItems.length < 2) return false

    // Find the minimum number of files in any column
    const minFileCount = Math.min(...batchFileItems.map((item) => item.files.length))

    // Valid if we have at least one file in each column
    return minFileCount > 0
  }

  useEffect(() => {
    // Start with one empty file slot
    if (fileItems.length === 0) {
      handleAddNewFile()
    }
  }, [])

  const handleProcessBatch = async () => {
    if (batchFiles.length === 0) {
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
      const results: string[] = []

      // Process each file individually
      for (let i = 0; i < batchFiles.length; i++) {
        if (controller.signal.aborted) {
          console.log("Batch processing aborted")
          break
        }
        const fileItem = batchFiles[i]

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
        const response = await VeradocService.processRagChecklist(
          {
            questions: requestData.questions,
            knowledgeBaseId: requestData.knowledgeBaseId,
            formData: {
              files: requestData.files,
              handwritten_files: requestData.handwrittenFiles,
            },
          },
          { signal: controller.signal },
        )

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
    } catch (error) {
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
    table: (props) => (
      <Box
        as="table"
        width="full"
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        {...props}
      />
    ),
    thead: (props) => <Box as="thead" bg="gray.100" {...props} />,
    tbody: (props) => <Box as="tbody" {...props} />,
    tr: (props) => <Box as="tr" {...props} />,
    th: (props) => (
      <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
    ),
    td: (props) => <Box as="td" p={4} borderBottomWidth="1px" {...props} />,
  }

  // Update your refetch logic when a new evaluation is created
  useEffect(() => {
    if (!loading && !batchLoading) {
      historyQuery.refetch()
    }
  }, [loading, batchLoading])

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
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text fontWeight="medium">Processing batch files...</Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <div aria-label="Knowledge Base and Checklist Selection">
          <VStack gap={4} align="stretch">
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
          </VStack>

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
        </div>

        {/* 3. Document Input */}
        <VStack
          align="stretch"
          mb={4}
          opacity={!selectedKnowledgeBase || !selectedChecklist ? 0.3 : 1}
          pointerEvents={!selectedKnowledgeBase || !selectedChecklist ? "none" : "auto"}
        >
          <Separator mb={3} />
          <Heading size="md" mb={0} textAlign="center">
            3. Upload document
          </Heading>
          <VStack gap={4} align="stretch">
            <Separator mb={3} />
          </VStack>

          {/* Mode Toggle */}
          <Field>
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
          </Field>

          {/* Conditional Rendering Based on Mode */}
          {mode === "manual" ? (
            <VStack spacing={4} align="stretch">
              {/* Manual Mode UI */}
              {fileItems.map((fileItem, index) => (
                <FileDropzone
                  key={index}
                  index={index}
                  fileItem={fileItem}
                  onUpdate={updateFile}
                  onRemove={removeFile}
                  onToggleHandwritten={toggleHandwritten}
                />
              ))}

              <HStack spacing={4}>
                <Button
                  variant="solid"
                  onClick={handleRun}
                  isDisabled={
                    fileItems.length < 1 ||
                    !questions.trim() ||
                    !fileItems.some((item) => item.file.size > 0)
                  }
                  loading={loading}
                >
                  Run
                </Button>
              </HStack>

              <Separator my={4} />
              <Heading size="md" mb={4}>
                Results
              </Heading>

              {/* Fixed layout with consistent side-by-side panels */}
              <Box display="flex" flexDirection={{ base: "column", md: "row" }} gap={4}>
                {/* History Panel - Always show this */}
                <Card.Root width={{ base: "100%", md: "300px" }} height="fit-content">
                  <Card.Header>
                    <Heading size="sm">Previous Evaluations</Heading>
                  </Card.Header>
                  <Card.Body p={2}>
                    <VStack align="stretch" spacing={2} maxH="500px" overflowY="auto">
                      {isHistoryLoading ? (
                        <Spinner size="sm" />
                      ) : !reportHistory || reportHistory.length === 0 ? (
                        <>
                          <Text fontSize="sm" color="gray.500">
                            No previous evaluations
                          </Text>
                        </>
                      ) : (
                        reportHistory.map((report) => (
                          <Box
                            key={report?.id}
                            p={3}
                            borderWidth="1px"
                            borderRadius="md"
                            cursor="pointer"
                            bg={selectedHistoryReport?.id === report?.id ? "blue.50" : "white"}
                            _hover={{ bg: "blue.50" }}
                            onClick={() => report?.id && loadReportFromHistory(report.id)}
                          >
                            <VStack align="start" spacing={1} width="100%">
                              <HStack spacing={1} width="100%" justify="space-between">
                                <Text fontSize="xs" color="gray.500">
                                  {report?.date_created
                                    ? format(new Date(report.date_created), "MMM d, yyyy")
                                    : "Unknown date"}
                                </Text>
                                {report?.qa_count > 0 && (
                                  <Text fontSize="xs" color="gray.500">
                                    {report.qa_count} question{report.qa_count !== 1 ? "s" : ""}
                                  </Text>
                                )}
                              </HStack>

                              {/* Document name with icon */}
                              <HStack spacing={1} width="100%">
                                <Box as={FiFileText} size="12px" color="blue.500" />
                                <Text fontWeight="medium" fontSize="sm" noOfLines={1}>
                                  {report.document_name || "Unnamed document"}
                                </Text>
                              </HStack>

                              {/* KB name with icon */}
                              {report?.kb_name && (
                                <HStack spacing={1} width="100%">
                                  <Box as={FiFileText} size="12px" color="blue.500" />
                                  <Text fontWeight="medium" fontSize="sm" noOfLines={1}>
                                    {report.document_name || "Unnamed document"}
                                  </Text>
                                </HStack>
                              )}

                              {/* KB name with icon */}
                              {report?.kb_name && (
                                <HStack spacing={1} width="100%">
                                  <Box as={FiDatabase} size="12px" color="gray.500" />
                                  <Text fontSize="xs" color="gray.600" noOfLines={1}>
                                    {report.kb_name}
                                  </Text>
                                </HStack>
                              )}
                            </VStack>
                          </Box>
                        ))
                      )}
                    </VStack>
                  </Card.Body>
                </Card.Root>

                {/* Results Panel - Always take remaining space */}
                <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
                  {/* Title for Results */}
                  <Heading size="md" mb={4}>
                    {selectedHistoryReport
                      ? `Evaluation from ${format(new Date(selectedHistoryReport.date_created), "MMM d, yyyy")} - ${selectedHistoryReport.document_name}`
                      : "Results"}
                  </Heading>

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
                    {results ? (
                      <>
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                          {results}
                        </ReactMarkdown>

                        {selectedHistoryReport?.id && (
                          <Box
                            position="sticky"
                            bottom={4}
                            right={4}
                            display="flex"
                            justifyContent="flex-end"
                            pointerEvents="auto"
                            zIndex={10}
                          >
                            <FeedbackButtons
                              interactionId={selectedHistoryReport.id}
                              onFeedbackSubmitted={(type) => {
                                showSuccessToast(`Thank you for marking this response as ${type}!`)
                              }}
                            />
                          </Box>
                        )}

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
                                  <Accordion.Root type="single" collapsible mt={2}>
                                    <Accordion.Item>
                                      <h2>
                                        <Accordion.ItemTrigger
                                          bg="gray.100"
                                          _hover={{ bg: "gray.200" }}
                                        >
                                          <Box flex="1" textAlign="left" fontWeight="medium">
                                            <HStack>
                                              <FiFileText />
                                              <Text>
                                                View Source Citations (
                                                {pair.source_citations.length})
                                              </Text>
                                            </HStack>
                                          </Box>
                                        </Accordion.ItemTrigger>
                                      </h2>
                                      <Accordion.ItemContent pb={4} bg="gray.50">
                                        {pair.source_citations.map((citation, cIndex) => (
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
                                                fileName={getDisplayFileName(
                                                  citation.metadata.source,
                                                )}
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
          ) : (
            <VStack spacing={4} align="stretch">
              {/* File Upload Area */}
              <Box
                border="2px dashed"
                borderColor="gray.300"
                borderRadius="md"
                p={6}
                textAlign="center"
                cursor="pointer"
                _hover={{ borderColor: "blue.500", bg: "blue.50" }}
                {...getRootProps()} // Use useDropzone directly in the component
              >
                <input {...getInputProps()} />
                <VStack spacing={2}>
                  <Text>Drag and drop files here, or click to browse</Text>
                  <Text fontSize="sm" color="gray.500">
                    You can upload multiple files at once
                  </Text>
                </VStack>
              </Box>

              {/* Uploaded Files List */}
              {batchFiles.length > 0 && (
                <Box>
                  <Text fontWeight="medium" mb={2}>
                    Uploaded Files ({batchFiles.length})
                  </Text>
                  <VStack align="stretch" spacing={2} maxH="300px" overflowY="auto">
                    {batchFiles.map((fileItem, index) => (
                      <HStack
                        key={fileItem.file.name + index} // More reliable key
                        justify="space-between"
                        bg="white"
                        p={3}
                        borderRadius="md"
                        border="1px solid"
                        borderColor="gray.200"
                      >
                        <Box>
                          <Text fontWeight="medium" noOfLines={1}>
                            {fileItem.file.name}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {(fileItem.file.size / 1024).toFixed(1)} KB
                          </Text>
                        </Box>
                        <HStack>
                          <ChakraField.Root display="flex" alignItems="center" width="auto">
                            <ChakraField.Label
                              htmlFor={`batch-handwritten-${index}`}
                              mb="0"
                              fontSize="sm"
                            >
                              Handwritten
                            </ChakraField.Label>
                            <Switch.Root id={`batch-handwritten-${index}`} colorPalette="blue">
                              <Switch.HiddenInput
                                checked={fileItem.isHandwritten}
                                onChange={() => {
                                  setBatchFiles((prev) =>
                                    prev.map((item, i) =>
                                      i === index
                                        ? { ...item, isHandwritten: !item.isHandwritten }
                                        : item,
                                    ),
                                  )
                                }}
                              />
                              <Switch.Control>
                                <Switch.Thumb />
                              </Switch.Control>
                            </Switch.Root>
                          </ChakraField.Root>
                          <Button
                            size="sm"
                            colorPalette="red"
                            onClick={(e) => {
                              setBatchFiles((prev) => prev.filter((_, i) => i !== index))
                            }}
                          >
                            Remove
                          </Button>
                        </HStack>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Results Panel - Always take remaining space */}
              <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
                {/* Title for Results */}
                <HStack justify="space-between" align="center" mb={4}>
                  <Heading size="md">
                    {selectedHistoryReport
                      ? `Evaluation from ${format(new Date(selectedHistoryReport.date_created), "MMM d, yyyy")} - ${selectedHistoryReport.document_name}`
                      : results
                        ? "Evaluation Results"
                        : ""}
                  </Heading>

                  {/* Add Copy and Download buttons */}
                  {results && (
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        variant="outline"
                        leftIcon={copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                        onClick={handleCopyReport}
                        colorPalette={copySuccess ? "green" : "blue"}
                      >
                        {copySuccess ? "Copied!" : "Copy Text"}
                      </Button>

                      <Button
                        size="sm"
                        variant="outline"
                        leftIcon={<FiDownload />}
                        onClick={handleDownloadReport}
                        isLoading={loadingDownload}
                        loadingText="Downloading..."
                        colorPalette="green"
                      >
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
                  maxH="400px"
                  overflowY="auto"
                  position="relative"
                  opacity={batchLoading ? 0.5 : 1}
                >
                  {batchLoading ? (
                    <Box
                      position="absolute"
                      top="50%"
                      left="50%"
                      transform="translate(-50%, -50%)"
                      zIndex="1"
                    >
                      <Spinner size="lg" color="blue.500" />
                    </Box>
                  ) : batchResults.length > 0 ? (
                    <>
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                        {results}
                      </ReactMarkdown>

                      {selectedHistoryReport?.id && (
                        <Box
                          position="sticky"
                          bottom={4}
                          right={4}
                          display="flex"
                          justifyContent="flex-end"
                          pointerEvents="auto"
                          zIndex={10}
                        >
                          <FeedbackButtons
                            interactionId={selectedHistoryReport.id}
                            onFeedbackSubmitted={(type) => {
                              showSuccessToast(`Thank you for marking this response as ${type}!`)
                            }}
                            existingFeedback={
                              selectedHistoryReport.feedback
                                ? {
                                    feedback: selectedHistoryReport.feedback.feedback as
                                      | "correct"
                                      | "incorrect"
                                      | null,
                                    feedbackText: selectedHistoryReport.feedback.feedbackText,
                                    feedbackDate: selectedHistoryReport.feedback.feedbackDate,
                                  }
                                : undefined
                            }
                          />
                        </Box>
                      )}

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
                                <Accordion.Root type="single" collapsible mt={2}>
                                  <Accordion.Item>
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
                                      {pair.source_citations.map((citation, cIndex) => (
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
                                              fileName={getDisplayFileName(
                                                citation.metadata.source,
                                              )}
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
                    <Text color="gray.500">Results will appear here after processing files.</Text>
                  )}
                </Box>
              </Box>
            </VStack>
          )}
        </VStack>
      </VStack>
    </Container>
  )
}

const FileDropzone = ({
  index,
  fileItem,
  onUpdate,
  onRemove,
  onToggleHandwritten,
}: {
  index: number
  fileItem: { file: File; isHandwritten: boolean }
  onUpdate: (index: number, file: File) => void
  onRemove: (index: number) => void
  onToggleHandwritten: (index: number) => void
}) => {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpdate(index, acceptedFiles[0])
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlchecklistats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/gif": [".gif"],
      "image/bmp": [".bmp"],
      "image/tiff": [".tif", ".tiff"],
      "image/webp": [".webp"],
    },
    multiple: false,
  })

  const { file, isHandwritten } = fileItem

  // Check if file is a placeholder
  const isPlaceholder = file && file.name === "placeholder" && file.size === 0

  return (
    <Box position="relative">
      <VStack align="stretch" spacing={2}>
        <Box
          {...getRootProps()}
          border="2px dashed"
          borderColor="gray.300"
          borderRadius="md"
          p={4}
          textAlign="center"
          cursor="pointer"
          _hover={{ borderColor: "blue.500" }}
        >
          <input {...getInputProps()} />
          <Text>
            {file && !isPlaceholder
              ? `Selected File: ${file.name}`
              : // commenting out a
                //: `Drag and drop File ${index + 1} here, or click to browse`}
                `Drag and drop a document to review here, or click to browse`}
          </Text>
        </Box>

        {/* Only show toggle if a real file is uploaded */}
        {file && !isPlaceholder && (
          <HStack justify="flex-end" px={2}>
            {/* <ChakraField.Root display="flex" alignItems="center" width="auto">
              <ChakraField.Label htmlFor={`handwritten-${index}`} mb="0" fontSize="sm">
                Analyze handwriting
              </ChakraField.Label>
              <Switch.Root id={`handwritten-${index}`} colorPalette="blue">
                <Switch.HiddenInput
                  checked={isHandwritten}
                  onChange={() => onToggleHandwritten(index)}
                />
                <Switch.Control>
                  <Switch.Thumb />
                </Switch.Control>
              </Switch.Root>
            </ChakraField.Root> */}

            <Button
              size="sm"
              colorPalette="red"
              onClick={(e) => {
                e.stopPropagation()
                onRemove(index)
              }}
            >
              Remove
            </Button>
          </HStack>
        )}
      </VStack>
    </Box>
  )
}

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/veradoc")({
  component: VeraDoc,
})
