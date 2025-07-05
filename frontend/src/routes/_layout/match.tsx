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
import { FiFileText } from "react-icons/fi"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import FileUpload, { FileItem } from "../../components/Common/FileUpload"
import FormTemplateTable from "../../components/Match/FormTemplateTable"

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
    mutationFn: (data: { fields: string; digitized_files: File[]; handwritten_files: File[] }) => {
      console.log("Now beginning mutation...")

      return FormconnectService.processForm({
        fields: data.fields,
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
