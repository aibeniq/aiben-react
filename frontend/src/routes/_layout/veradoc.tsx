import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Spinner,
  Accordion,
  Tabs,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import { CancelablePromise } from "@/client/core/CancelablePromise"
import SourceLink from "@/components/Common/SourceLink"
import FileUpload, { FileItem } from "@/components/Common/FileUpload"
import DownloadButton from "@/components/ui/download-button"
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
import { FiFileText, FiDatabase, FiCopy, FiCheck } from "react-icons/fi"
import KnowledgeBaseTable from "../../components/Common/KnowledgeBaseTable"
import ChecklistTable from "../../components/Review/ChecklistTable"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"

const VeraDoc = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])
  const abortControllerRef = useRef<AbortController | null>(null)
  const ongoingRequest = useRef<CancelablePromise<any> | null>(null)

  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [showChecklistModal, setShowChecklistModal] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)

  const [questions, setQuestions] = useState("")

  const [fileItems, setFileItems] = useState<FileItem[]>([])

  const [results, setResults] = useState<
    Array<{ filename: string; displayResults: string; qaPairs: any[] }>
  >([])
  const [loading, setLoading] = useState<boolean>(false)
  const [activeTab, setActiveTab] = useState<number>(0)

  const [checklists, setChecklists] = useState<VeraDocChecklist[]>([])
  const [selectedChecklist, setSelectedChecklist] = useState<VeraDocChecklist | null>(null)

  // Reset active tab when results change
  useEffect(() => {
    if (results.length > 0) {
      setActiveTab(0)
    }
  }, [results.length])

  const handleCopyReport = async () => {
    try {
      const activeTabIndex = activeTab
      const activeResult = results[activeTabIndex]

      if (!activeResult) {
        showErrorToast("No active result to copy")
        return
      }

      let fullText = `# Evaluation Summary\n\n`

      // Add the active result's display content and QA pairs
      fullText += activeResult.displayResults + "\n\n"

      activeResult.qaPairs.forEach((pair, pairIndex) => {
        fullText += `## Question ${pairIndex + 1}: ${pair.question}\n\n`
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

      const activeTabIndex = activeTab
      const activeResult = results[activeTabIndex]

      if (!activeResult) {
        showErrorToast("No active result to download")
        return
      }

      let fullText = `# Evaluation Summary\n\n`
      fullText += activeResult.displayResults + "\n\n"

      activeResult.qaPairs.forEach((pair, pairIndex) => {
        fullText += `## Question ${pairIndex + 1}: ${pair.question}\n\n`
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
      const filename = activeResult.filename.replace(/[^a-zA-Z0-9]/g, "_")
      a.href = url
      a.download = `Evaluation_${filename}_${timestamp}.docx`
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

  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        const response = await KnowledgeBasesService.readKnowledgeBases({
          skip: 0,
          limit: 100,
        })
        setKnowledgeBases(response.data || [])
      } catch (error) {
        console.error("Error fetching knowledge bases:", error)
      }
    }

    fetchKnowledgeBases()
  }, [])

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

      const singleResult = {
        filename: data.results.filename,
        displayResults: data.results.final_evaluation || "",
        qaPairs: (data.results.qa_pairs as any[]) || [],
      }

      setResults([singleResult])
    },
    onError: (error) => {
      console.log("RAG mutation unsuccessful!")
      // Convert error to array format
      const errorResult = {
        filename: "Error",
        displayResults: `Error: ${error.message}`,
        qaPairs: [],
      }
      setResults([errorResult])
    },
    onSettled: () => {
      ongoingRequest.current = null
      setLoading(false)
    },
  })

  const handleRun = async () => {
    if (fileItems.length < 1) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please upload at least one file.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!questions.trim()) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please enter at least one question.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!selectedKnowledgeBase) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please select a knowledge base for context.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    // Filter out placeholder files and separate into regular vs handwritten
    const validItems = fileItems.filter((item) => item.file.size > 0)
    const regularFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)
    const handwrittenFiles = validItems
      .filter((item) => item.isHandwritten)
      .map((item) => item.file)

    if (validItems.length < 1) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please upload at least one valid file.",
        qaPairs: [],
      }
      setResults([errorResult])
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
      const errorResult = {
        filename: "Error",
        displayResults: "Error: Please upload at least one file for batch processing.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!questions.trim()) {
      const errorResult = {
        filename: "Error",
        displayResults: "Error: Please enter at least one question.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!selectedKnowledgeBase) {
      const errorResult = {
        filename: "Error",
        displayResults: "Error: Please select a knowledge base for context.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    // Clear previous results
    setResults([])
    setLoading(true)

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
      const batchResults: Array<{
        filename: string
        displayResults: string
        qaPairs: any[]
      }> = []

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

        let displayResults = ""

        if (response.results.final_evaluation) {
          displayResults += "## FINAL EVALUATION\n\n"
          displayResults += response.results.final_evaluation + "\n\n"
        }

        // Store the QA pairs in the results array
        batchResults.push({
          filename: fileItem.file.name,
          displayResults,
          qaPairs: (response.results.qa_pairs as any[]) || [],
        })

        // Update your state for batch results
        setResults([...batchResults])
      }
    } catch (error: any) {
      // Handle errors, checking if it's an abort
      if (error.name === "AbortError") {
        console.log("Batch processing was aborted")
      } else {
        console.error("Batch processing error:", error)
        const errorResult = {
          filename: "Error",
          displayResults: `Error processing batch: ${error.message}`,
          qaPairs: [],
        }
        setResults([errorResult])
      }
    } finally {
      setLoading(false)
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

  // Function to render results content
  const renderResultsContent = (
    result: { displayResults: string; qaPairs: any[] },
    resultIndex: number,
  ) => (
    <Box key={resultIndex}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {result.displayResults}
      </ReactMarkdown>

      {result.qaPairs.map((pair, pairIndex) => (
        <Box
          key={`${resultIndex}-${pairIndex}`}
          mt={4}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg="white"
        >
          <Heading as="h3" size="md" mb={2}>
            Question {pairIndex + 1}: {pair.question}
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
              <Accordion.Item value={`citations-${resultIndex}-${pairIndex}`}>
                <h2>
                  <Accordion.ItemTrigger bg="gray.100" _hover={{ bg: "gray.200" }}>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      <HStack>
                        <FiFileText />
                        <Text>View Source Citations ({pair.source_citations.length})</Text>
                      </HStack>
                    </Box>
                  </Accordion.ItemTrigger>
                </h2>
                <Accordion.ItemContent pb={4} bg="gray.50">
                  {pair.source_citations.map((citation: any, cIndex: number) => (
                    <Box key={cIndex} p={3} mb={2} borderWidth="1px" borderRadius="md" bg="white">
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
                        <Text as="span" ml={1} fontWeight="normal" color="blue.600">
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
  )

  return (
    <Container maxW="container.xl" py={8}>
      {/* Add this overlay spinner that shows when loading is true */}
      {loading && (
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
            <Text fontWeight="medium">
              {fileItems.length > 1 ? "Processing files..." : "Processing file..."}
            </Text>
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
              onClick={() => setShowChecklistModal(true)}
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
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={!selectedKnowledgeBase || !selectedChecklist ? 0.3 : 1}
          pointerEvents={!selectedKnowledgeBase || !selectedChecklist ? "none" : "auto"}
        >
          <HStack gap={4} justify="center">
            <Button
              variant="solid"
              onClick={fileItems.length > 0 ? handleProcessBatch : handleRun}
              disabled={
                fileItems.length < 1 ||
                !questions.trim() ||
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
              Run
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
              <HStack justify="space-between" align="center" mb={4}>
                <Heading size="md">
                  {fileItems.length > 1 ? "Batch Processing Results" : "Results"}
                </Heading>

                {results.length > 0 && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyReport}
                      colorPalette={copySuccess ? "rgba(0, 65, 72, 0.9)" : "blue"}
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess ? "Copied!" : "Copy Text"}
                    </Button>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadReport}
                      loading={loadingDownload}
                    >
                      Download DOCX
                    </DownloadButton>
                  </HStack>
                )}
              </HStack>

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
                {results.length > 0 ? (
                  <>
                    <Tabs.Root
                      defaultValue="0"
                      value={activeTab.toString()}
                      onValueChange={(details) => setActiveTab(parseInt(details.value))}
                    >
                      <Tabs.List>
                        {results.map((result, index) => {
                          const fileName = result.filename

                          return (
                            <Tabs.Trigger key={index} value={index.toString()}>
                              {fileName.length > 30 ? `${fileName.slice(0, 30)}...` : fileName}
                            </Tabs.Trigger>
                          )
                        })}
                      </Tabs.List>

                      {results.map((result, index) => (
                        <Tabs.Content key={index} value={index.toString()}>
                          {renderResultsContent(result, index)}
                        </Tabs.Content>
                      ))}
                    </Tabs.Root>
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
