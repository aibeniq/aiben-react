import { Box, Button, Container, Heading, Text, VStack, HStack, Spinner } from "@chakra-ui/react"
import { useState, useEffect } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import {
  FormconnectService,
  FormConnectForm,
  KnowledgeBasesService,
  KnowledgeBasePublic,
} from "@/client"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FiFileText, FiCopy, FiCheck } from "react-icons/fi"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import FileUpload, { FileItem } from "../../components/Common/FileUpload"
import FormTemplateTable from "../../components/Match/FormTemplateTable"
import SearchModeToggle from "../../components/Common/SearchModeToggle"
import DownloadButton from "../../components/ui/download-button"
import useCustomToast from "../../hooks/useCustomToast"

const FormConnect = () => {
  const [fileItems, setFileItems] = useState<FileItem[]>([])
  const [forms, setForms] = useState<FormConnectForm[]>([])
  const [selectedForm, setSelectedForm] = useState<FormConnectForm | null>(null)
  const [formName, setFormName] = useState("")
  const [formDescription, setFormDescription] = useState("")
  const [fields, setFields] = useState("")
  const [results, setResults] = useState("")
  const [loading, setLoading] = useState(false)
  const [showFormModal, setShowFormModal] = useState(false)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  
  const { showSuccessToast, showErrorToast } = useCustomToast()

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
      console.log("Response data:", data)
      // Handle both comparison and single file responses
      if (data.results.comparison) {
        console.log("Comparison data:", data.results.comparison)
        setResults(data.results.comparison as string)
      } else if (data.results.message) {
        setResults(
          `${data.results.message}\n\n${JSON.stringify(data.results.extracted_data, null, 2)}`,
        )
      } else {
        setResults(JSON.stringify(data.results, null, 2))
      }
    },
    onError: (error: any) => {
      console.log("Mutation unsuccessful!")
      setResults(`Error: ${error.message}`)
    },
  })

  const handleRun = async () => {
    if (fileItems.length < 1) {
      setResults("Please upload at least one file.")
      return
    }

    if (!fields.trim()) {
      setResults("Please enter at least one field.")
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

  const handleCopyResults = async () => {
    try {
      await navigator.clipboard.writeText(results)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast("Results copied to clipboard")
    } catch (err) {
      console.error("Failed to copy results:", err)
      showErrorToast("Failed to copy results to clipboard")
    }
  }

  const handleDownloadResults = async () => {
    try {
      setLoadingDownload(true)

      if (!results) {
        showErrorToast("No results to download")
        return
      }

      const response = await FormconnectService.generateDocx({
        requestBody: { content: results },
      })

      console.log("Received DOCX response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)
      console.log("Response instanceof ArrayBuffer:", response instanceof ArrayBuffer)

      let blob
      if (response instanceof Blob) {
        console.log("Response is already a Blob")
        blob = response
      } else if (response instanceof ArrayBuffer) {
        console.log("Converting ArrayBuffer to Blob")
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        console.log("Converting unknown response type to Blob")
        blob = new Blob([response as any], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }

      console.log("Final DOCX blob:", blob)
      console.log("Blob size:", blob.size)
      console.log("Blob type:", blob.type)

      const url = window.URL.createObjectURL(blob)
      console.log("Created DOCX object URL:", url)

      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url
      a.download = `form_processing_${timestamp}.docx`

      console.log("DOCX download filename:", `form_processing_${timestamp}.docx`)
      console.log("About to trigger DOCX download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("DOCX download triggered successfully")
      showSuccessToast("Document downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download document:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(`Failed to download document: ${err.message || "Unknown error"}`)
    } finally {
      console.log("DOCX download process completed")
      setLoadingDownload(false)
    }
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title="Form Template"
              description={selectedForm ? selectedForm.name : "Click to select"}
              icon={<FiFileText size={24} />}
              isSelected={!!selectedForm}
              onClick={() => setShowFormModal(true)}
            />

            <FileUpload
              files={fileItems}
              onFilesChange={setFileItems}
              showHandwrittenToggle={true}
            />

            <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />
          </VStack>
        </HStack>

        <SelectionModal
          isOpen={showFormModal}
          onClose={() => setShowFormModal(false)}
          title="Select Form Template"
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
          opacity={!selectedForm ? 0.3 : 1}
          pointerEvents={!selectedForm ? "none" : "auto"}
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
              Match
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
                <Heading size="md">Results</Heading>

                {results && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyResults}
                      colorPalette={copySuccess ? "green" : "blue"}
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess ? "Copied!" : "Copy Text"}
                    </Button>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadResults}
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
                {results ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{results}</ReactMarkdown>
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
export const Route = createFileRoute("/_layout/match")({
  component: FormConnect,
})
