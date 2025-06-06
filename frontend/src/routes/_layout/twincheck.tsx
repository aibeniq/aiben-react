import { useState, useEffect } from "react"
import {
  Box,
  Button,
  Container,
  Heading,
  HStack,
  Text,
  VStack,
  Input,
  Textarea,
  Spinner,
  Separator,
  Accordion,
} from "@chakra-ui/react"
import { FiUpload, FiFile, FiFileText, FiCheck, FiCopy } from "react-icons/fi"
import { useDropzone } from "react-dropzone"
import { format } from "date-fns"
import { createFileRoute } from "@tanstack/react-router"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { TwincheckService } from "@/client"
import { useMutation, useQuery } from "@tanstack/react-query"
import { InteractiveList } from "@/components/ui/interactive-list"
import { Field } from "@/components/ui/Field"
import useCustomToast from "@/hooks/useCustomToast"
import FeedbackButtons from "@/components/Feedback/FeedbackButtons"
import SourceLink from "@/components/Common/SourceLink"
import FileUpload, { FileItem } from "@/components/Common/FileUpload"
import DownloadButton from "@/components/ui/download-button"
import { CancelablePromise } from "@/client/core/CancelablePromise"

const TwinCheck = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)

  // File state
  const [document1, setDocument1] = useState<File | null>(null)
  const [document2, setDocument2] = useState<File | null>(null)

  // Topics state
  const [topics, setTopics] = useState("")
  const [comparisons, setComparisons] = useState([]) // List of saved comparison topics
  const [selectedComparison, setSelectedComparison] = useState(null) // Currently selected comparison
  const [comparisonName, setComparisonName] = useState("") // Name of the comparison being created/edited
  const [comparisonDescription, setComparisonDescription] = useState("") // Description of the comparison

  // Results state
  const [summary, setSummary] = useState("")
  const [topicResults, setTopicResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedTopic, setExpandedTopic] = useState<number | null>(null)

  // Function to copy report to clipboard
  const handleCopyReport = async () => {
    try {
      // Prepare combined text with summary and all topic analyses
      let fullText = `# Summary\n\n${summary}\n\n# Topic Analysis\n\n`

      // Add each topic and its analysis
      topicResults.forEach((topic, index) => {
        fullText += `## Topic: ${topic.topic}\n\n${topic.analysis}\n\n`
      })

      await navigator.clipboard.writeText(fullText)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast("Comparison results copied to clipboard")
    } catch (err) {
      console.error("Failed to copy report:", err)
      showErrorToast("Failed to copy report to clipboard")
    }
  }

  // Function to download report as DOCX
  const handleDownloadReport = async () => {
    try {
      setLoadingDownload(true)

      // Prepare combined text with summary and all topic analyses
      let fullText = `# Summary\n\n${summary}\n\n# Topic Analysis\n\n`

      // Add each topic and its analysis
      topicResults.forEach((topic, index) => {
        fullText += `## Topic: ${topic.topic}\n\n${topic.analysis}\n\n`
      })

      // Create a unique document name with document titles if available
      const doc1Name = document1?.name || "Document1"
      const doc2Name = document2?.name || "Document2"
      const docTitle = `Comparison of ${doc1Name} and ${doc2Name}`

      const response = await TwincheckService.generateDocx({
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
      a.download = `comparison_${timestamp}.docx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast("Comparison downloaded successfully")
    } catch (err) {
      console.error("Failed to download report:", err)
      showErrorToast(`Failed to download report: ${err.message || "Unknown error"}`)
    } finally {
      setLoadingDownload(false)
    }
  }

  // Fetch saved comparison topic sets when component mounts
  useEffect(() => {
    const fetchComparisons = async () => {
      try {
        const data = await TwincheckService.getComparisons()
        setComparisons(data)
      } catch (error) {
        console.error("Error fetching comparisons:", error)
      }
    }

    fetchComparisons()
  }, [])

  // Mutation for comparing documents
  const mutation = useMutation({
    mutationFn: (data: { comparison_topics: string; document1: File; document2: File }) => {
      return TwincheckService.compareDocuments({
        comparisonTopics: data.comparison_topics,
        formData: {
          document1: data.document1,
          document2: data.document2,
        },
      })
    },
    onSuccess: (data) => {
      console.log("Response data:", data)

      setSummary(data.results.summary)
      setTopicResults(data.results.topic_analysis || [])
    },
    onError: (error) => {
      console.log("Comparison failed!")
      setSummary(`Error: ${error.message}`)
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  const handleCompare = async () => {
    if (!document1) {
      showErrorToast("Please upload Document 1")
      return
    }

    if (!document2) {
      showErrorToast("Please upload Document 2")
      return
    }

    if (!topics.trim()) {
      showErrorToast("Please enter at least one comparison topic")
      return
    }

    const requestData = {
      comparison_topics: topics,
      document1: document1,
      document2: document2,
    }

    setLoading(true)
    mutation.mutate(requestData)
  }

  // Custom components for markdown rendering
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

  return (
    <Container maxW="container.xl" py={8}>
      {/* Loading overlay */}
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
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text fontWeight="medium">Processing documents comparison...</Text>
          </VStack>
        </Box>
      )}

      <VStack spacing={6} align="stretch">
        {/* Document Upload Section */}
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>
            Document Selection
          </Heading>

          <HStack spacing={6} align="stretch">
            {/* Document 1 Upload */}
            <Box flex="1">
              <FileUploader
                label="Document 1"
                file={document1}
                setFile={setDocument1}
                accept={{
                  "application/pdf": [".pdf"],
                  "text/plain": [".txt"],
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
                    ".docx",
                  ],
                }}
              />
            </Box>

            {/* Document 2 Upload */}
            <Box flex="1">
              <FileUploader
                label="Document 2"
                file={document2}
                setFile={setDocument2}
                accept={{
                  "application/pdf": [".pdf"],
                  "text/plain": [".txt"],
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
                    ".docx",
                  ],
                }}
              />
            </Box>
          </HStack>
        </VStack>

        <Separator my={4} />

        {/* Comparison Topics Selection and Management */}
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>
            Comparison Topics
          </Heading>

          <Field label="Saved Topic Lists">
            <select
              value={selectedComparison?.id || ""}
              onChange={(e) => {
                const comparison = comparisons.find((c) => c.id === e.target.value)
                setSelectedComparison(comparison)
                setTopics(comparison?.topics || "")
                setComparisonName(comparison?.name || "")
                setComparisonDescription(comparison?.description || "")
              }}
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "0.375rem",
                borderColor: "#E2E8F0",
              }}
            >
              <option value="">Select a saved topic list</option>
              {comparisons.map((comparison) => (
                <option key={comparison.id} value={comparison.id}>
                  {comparison.name}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Topic List Name" required>
            <Input
              value={comparisonName}
              onChange={(e) => setComparisonName(e.target.value)}
              placeholder="Enter topic list name"
            />
          </Field>

          <Field label="Topic List Description">
            <Textarea
              value={comparisonDescription}
              onChange={(e) => setComparisonDescription(e.target.value)}
              placeholder="Enter comparison description"
              resize="vertical"
            />
          </Field>

          <Field label="Comparison Topics" required borderTop="1px solid" py={4}>
            <InteractiveList
              value={topics}
              onChange={setTopics}
              placeholder="Add comparison topic"
              minItems={1}
            />
          </Field>

          <HStack spacing={4} pt={2}>
            <Button
              variant="solid"
              onClick={async () => {
                try {
                  if (selectedComparison) {
                    // Update existing comparison
                    await TwincheckService.updateComparison({
                      comparisonId: selectedComparison.id,
                      requestBody: {
                        name: comparisonName,
                        description: comparisonDescription,
                        topics: topics,
                      },
                    })
                    showSuccessToast("Topic list updated successfully")
                  } else {
                    // Create new comparison
                    await TwincheckService.createComparison({
                      requestBody: {
                        name: comparisonName,
                        description: comparisonDescription,
                        topics: topics,
                      },
                    })
                    showSuccessToast("Topic list saved successfully")
                  }

                  // Clear the comparison fields and re-fetch the list of comparisons
                  setComparisonName("")
                  setComparisonDescription("")
                  setTopics("")
                  setSelectedComparison(null)

                  // Fetch the latest comparisons
                  const updatedComparisons = await TwincheckService.getComparisons()
                  setComparisons(updatedComparisons)
                } catch (error) {
                  console.error("Error saving topic list:", error)
                  showErrorToast("Failed to save topic list. Please try again.")
                }
              }}
            >
              {selectedComparison ? "Update Topic List" : "Save Topic List"}
            </Button>

            <Button
              variant="subtle"
              colorPalette="blue"
              onClick={async () => {
                if (!selectedComparison) {
                  showErrorToast("Please select a topic list to copy.")
                  return
                }

                try {
                  // Create a copy of the selected comparison
                  await TwincheckService.createComparison({
                    requestBody: {
                      name: `${selectedComparison.name} (Copy)`,
                      description: selectedComparison.description,
                      topics: selectedComparison.topics,
                    },
                  })
                  showSuccessToast("Comparison copied successfully")

                  // Re-fetch the list of comparisons
                  const updatedComparisons = await TwincheckService.getComparisons()
                  setComparisons(updatedComparisons)
                } catch (error) {
                  console.error("Error copying comparison:", error)
                  showErrorToast("Failed to copy comparison. Please try again.")
                }
              }}
              isDisabled={!selectedComparison}
            >
              Copy Topic List
            </Button>

            <Button
              variant="subtle"
              colorPalette="red"
              onClick={async () => {
                if (!selectedComparison) {
                  showErrorToast("Please select a comparison to delete.")
                  return
                }

                try {
                  await TwincheckService.deleteComparison({ comparisonId: selectedComparison.id })

                  // Remove the deleted comparison from the list
                  setComparisons((prev) =>
                    prev.filter((comparison) => comparison.id !== selectedComparison.id),
                  )

                  // Clear the selected comparison
                  setSelectedComparison(null)
                  setComparisonName("")
                  setComparisonDescription("")
                  setTopics("")

                  showSuccessToast("Comparison deleted successfully")
                } catch (error) {
                  console.error("Error deleting comparison:", error)
                  showErrorToast("Failed to delete comparison. Please try again.")
                }
              }}
              isDisabled={!selectedComparison}
            >
              Delete Topic List
            </Button>
          </HStack>

          {/* Compare Button */}
          <Button
            mt={4}
            variant="solid"
            colorPalette="green"
            size="lg"
            onClick={handleCompare}
            isDisabled={!document1 || !document2 || !topics.trim()}
            isLoading={loading}
          >
            Compare Documents
          </Button>
        </VStack>

        {/* Results Section */}
        <Separator my={4} />

        <HStack justify="space-between" align="center" mb={4}>
          <Heading size="md">Comparison Results</Heading>

          {/* Copy and download buttons */}
          {summary && (
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

              <DownloadButton size="sm" onClick={handleDownloadReport} loading={loadingDownload}>
                Download DOCX
              </DownloadButton>
            </HStack>
          )}
        </HStack>

        <Box display="flex" flexDirection={{ base: "column", md: "row" }} gap={4}>
          {/* Results Content */}
          <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
            {summary || topicResults.length > 0 ? (
              <>
                <HStack justify="space-between" align="center" mb={4}>
                  <Heading size="md">Comparison Results</Heading>
                </HStack>

                <Box
                  border="1px solid"
                  borderColor="gray.200"
                  borderRadius="md"
                  p={4}
                  bg="white"
                  minH="100px"
                  overflowY="auto"
                >
                  {/* Summary Section */}
                  <Heading as="h3" size="md" mb={2}>
                    Summary
                  </Heading>
                  <Box p={3} mb={4} borderWidth="1px" borderRadius="md" bg="gray.50">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {summary}
                    </ReactMarkdown>
                  </Box>

                  {/* Topic Analysis Section */}
                  {topicResults.length > 0 && (
                    <Box mt={8}>
                      <Heading as="h3" size="md" mb={4}>
                        Topic Analysis
                      </Heading>

                      {topicResults.map((topicResult, index) => (
                        <Box
                          key={index}
                          mb={6}
                          p={5}
                          borderWidth="1px"
                          borderRadius="md"
                          bg={expandedTopic === index ? "gray.50" : "white"}
                          _hover={{ bg: "gray.50" }}
                        >
                          <Heading
                            as="h4"
                            size="sm"
                            mb={3}
                            onClick={() => setExpandedTopic(expandedTopic === index ? null : index)}
                            cursor="pointer"
                            display="flex"
                            alignItems="center"
                          >
                            <Box
                              as="span"
                              mr={2}
                              transform={expandedTopic === index ? "rotate(90deg)" : "rotate(0deg)"}
                              transition="transform 0.2s"
                            >
                              ▶
                            </Box>
                            Topic: {topicResult.topic}
                          </Heading>

                          {expandedTopic === index && (
                            <Box mb={4} p={3} borderLeft="4px solid" borderColor="blue.200">
                              <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                                {topicResult.analysis}
                              </ReactMarkdown>
                            </Box>
                          )}
                        </Box>
                      ))}
                    </Box>
                  )}
                </Box>
              </>
            ) : (
              <Box
                border="1px dashed"
                borderColor="gray.300"
                borderRadius="md"
                p={8}
                bg="gray.50"
                minH="300px"
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                textAlign="center"
              >
                <Box fontSize="5xl" color="gray.300" mb={4}>
                  <FiFileText />
                </Box>
                <Heading size="md" mb={2} color="gray.600">
                  No Comparison Results
                </Heading>
                <Text color="gray.500" mb={4} maxW="400px">
                  Upload two documents and define comparison topics to start a new comparison.
                </Text>
              </Box>
            )}
          </Box>
        </Box>
      </VStack>
    </Container>
  )
}

// File uploader component
const FileUploader = ({
  label,
  file,
  setFile,
  accept,
}: {
  label: string
  file: File | null
  setFile: (file: File) => void
  accept?: Record<string, string[]>
}) => {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0])
      }
    },
    accept,
    multiple: false,
  })

  return (
    <Box>
      <Text fontWeight="medium" mb={2}>
        {label}
      </Text>
      <Box
        {...getRootProps()}
        border="2px dashed"
        borderColor="gray.300"
        borderRadius="md"
        p={4}
        textAlign="center"
        cursor="pointer"
        _hover={{ borderColor: "blue.500" }}
        bg={file ? "blue.50" : "transparent"}
        transition="all 0.2s"
      >
        <input {...getInputProps()} />
        <VStack spacing={2}>
          {file ? (
            <>
              <Box as={FiFile} color="blue.500" fontSize="2xl" />
              <Text fontWeight="medium">{file.name}</Text>
              <Text fontSize="sm" color="gray.600">
                {(file.size / 1024).toFixed(1)} KB
              </Text>
            </>
          ) : (
            <>
              <Box as={FiUpload} color="gray.400" fontSize="2xl" />
              <Text>Click to browse or drag & drop</Text>
              <Text fontSize="xs" color="gray.500">
                Supports PDF, TXT, and DOCX
              </Text>
            </>
          )}
        </VStack>
      </Box>
    </Box>
  )
}

export const Route = createFileRoute("/_layout/twincheck")({
  component: TwinCheck,
})
