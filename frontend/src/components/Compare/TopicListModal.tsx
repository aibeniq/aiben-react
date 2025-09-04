import { useState } from "react"
import {
  HStack,
  VStack,
  Input,
  Textarea,
  Dialog,
  Portal,
  CloseButton,
  Button,
  Text,
  IconButton,
  Box,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { TwinCheckTopicList, TwincheckService, KnowledgeBasePublic } from "../../client"
import TopicItem from "./TopicItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import FileUpload, { FileItem } from "../Common/FileUpload"
import SearchModeToggle from "../Common/SearchModeToggle"
import useCustomToast from "../../hooks/useCustomToast"
import { FiCopy } from "react-icons/fi"
import { copyToClipboard } from "../../utils/copyToClipboard"

interface TopicListModalProps {
  isOpen: boolean
  onClose: () => void
  editingTopicList: TwinCheckTopicList | null
  onSave: () => void
  topicListName: string
  setTopicListName: (name: string) => void
  topicListDescription: string
  setTopicListDescription: (description: string) => void
  topicsList: string[]
  updateTopic: (index: number, value: string) => void
  updateTopicsFromList: (newTopicsList: string[]) => void
  handleTopicBlur: (index: number, value: string) => void
  removeTopic: (index: number) => void
  moveTopicUp: (index: number) => void
  moveTopicDown: (index: number) => void
  knowledgeBases?: KnowledgeBasePublic[]
}

const TopicListModal = ({
  isOpen,
  onClose,
  editingTopicList,
  onSave,
  topicListName,
  setTopicListName,
  topicListDescription,
  setTopicListDescription,
  topicsList,
  updateTopic,
  updateTopicsFromList,
  handleTopicBlur,
  removeTopic,
  moveTopicUp,
  moveTopicDown,
  knowledgeBases = [],
}: TopicListModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Validation state
  const [validationErrors, setValidationErrors] = useState<{ [key: string]: string }>({})

  // Validation function
  const validateForm = () => {
    const errors: { [key: string]: string } = {}

    if (!topicListName.trim()) {
      errors.name = "Topic list name is required"
    } else if (topicListName.trim().length < 3) {
      errors.name = "Topic list name must be at least 3 characters long"
    }

    // Description is optional - no validation required

    if (topicsList.length === 0 || topicsList.every((topic) => !topic.trim())) {
      errors.topics = "At least one topic is required"
    }

    setValidationErrors(errors)

    // Show the first error as a toast
    const firstError = Object.values(errors)[0]
    if (firstError) {
      showErrorToast(firstError)
      return false
    }

    return true
  }

  // Clear validation errors when user starts typing
  const handleNameChange = (value: string) => {
    setTopicListName(value)
    if (validationErrors.name) {
      setValidationErrors((prev) => ({ ...prev, name: "" }))
    }
  }

  const handleDescriptionChange = (value: string) => {
    setTopicListDescription(value)
    if (validationErrors.description) {
      setValidationErrors((prev) => ({ ...prev, description: "" }))
    }
  }

  // Enhanced save handler with validation
  const handleSave = () => {
    if (!validateForm()) {
      return // Stop execution if validation fails
    }

    // Call the parent's onSave function if validation passes
    onSave()
  }

  const [suggesting, setSuggesting] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")

  // Remove the knowledge base effect
  // useEffect(() => {
  //   if (selectedKnowledgeBase) {
  //     setReferenceMode("knowledge-base")
  //   }
  // }, [selectedKnowledgeBase])

  const handleSuggestTopics = async () => {
    if (!topicListDescription.trim()) {
      showErrorToast("Please enter a topic list description first")
      return
    }

    // Validate minimum length requirement
    if (topicListDescription.trim().length < 10) {
      showErrorToast("Please enter a more detailed description (at least 10 characters)")
      return
    }

    setSuggesting(true)

    try {
      let response

      if (exampleFiles.length > 0) {
        // Use the existing file upload endpoint
        const files = exampleFiles.map((item) => item.file)
        response = await TwincheckService.generateTopics({
          formData: {
            description: topicListDescription.trim(),
            comparison_type: "general",
            files: files.length > 0 ? files : undefined,
          },
        })
      } else {
        // Use the basic file upload endpoint without files
        response = await TwincheckService.generateTopics({
          formData: {
            description: topicListDescription.trim(),
            comparison_type: "general",
          },
        })
      }

      // Replace current topics with suggested ones
      const suggestedTopics = response.topics || []
      if (suggestedTopics.length > 0) {
        // Replace the entire topics list with suggested topics plus an empty topic for user input
        const newTopicsList = [...suggestedTopics, ""]
        updateTopicsFromList(newTopicsList)

        // Clear topics validation error if it exists
        if (validationErrors.topics) {
          setValidationErrors((prev) => ({ ...prev, topics: "" }))
        }

        let successMessage = `Suggested ${suggestedTopics.length} topics from description`
        if (exampleFiles.length > 0) {
          successMessage += ` and ${exampleFiles.length} example file(s)`
        }

        showSuccessToast(successMessage)
      } else {
        showErrorToast("No topics were suggested. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error suggesting topics:", error)
      console.log("Error details:", {
        message: error.message,
        status: error.status,
        statusText: error.statusText,
        url: error.url,
        body: error.body,
        stack: error.stack,
      })

      // Handle specific error types
      if (error.status === 422) {
        showErrorToast(
          "Invalid request. Please check that your description meets the requirements.",
        )
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to suggest topics.")
      } else if (error.status === 404) {
        showErrorToast("Suggest topics feature is not available. Please contact support.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to suggest topics: ${error.message || "Unknown error"}`)
      }
    } finally {
      setSuggesting(false)
    }
  }

  // Handler for reference mode changes
  const handleReferenceModeChange = (mode: "files" | "knowledge-base") => {
    setReferenceMode(mode)
    // Clear the opposite mode's selection
    if (mode === "files") {
      setReferenceKnowledgeBase(null)
    } else {
      setExampleFiles([])
    }
  }

  const handleModalClose = () => {
    setExampleFiles([])
    onClose()
  }

  const handleCopyTopics = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Filter out empty topics
    const nonEmptyTopics = topicsList.filter((topic) => topic.trim() !== "")

    if (nonEmptyTopics.length === 0) {
      showErrorToast("No topics to copy")
      return
    }

    try {
      await copyToClipboard(nonEmptyTopics.join("\n"))
      showSuccessToast("Topics copied to clipboard!")
    } catch (error) {
      console.error("Error copying topics:", error)
      showErrorToast("Failed to copy topics to clipboard")
    }
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(e) => (e.open ? null : handleModalClose())}>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="4xl" maxH="90vh">
            <Dialog.Header>
              <Dialog.Title>
                {editingTopicList ? "Edit Topic List" : "Create New Topic List"}
              </Dialog.Title>
            </Dialog.Header>

            <Dialog.Body overflowY="auto">
              <VStack align="stretch" gap={4}>
                <HStack align="stretch" gap={4}>
                  <VStack align="stretch" gap={4} flex="1">
                    <Field
                      label="Topic List Name"
                      required
                      invalid={!!validationErrors.name}
                      errorText={validationErrors.name}
                    >
                      <Input
                        value={topicListName}
                        onChange={(e) => handleNameChange(e.target.value)}
                        placeholder="Enter topic list name"
                      />
                    </Field>

                    <Field
                      label="Topic List Description"
                      invalid={!!validationErrors.description}
                      errorText={validationErrors.description}
                    >
                      <Textarea
                        value={topicListDescription}
                        onChange={(e) => handleDescriptionChange(e.target.value)}
                        placeholder="Enter topic list description to auto-suggest topics (minimum 10 characters)..."
                        resize="vertical"
                        rows={3}
                      />
                      {topicListDescription.trim().length > 0 &&
                        topicListDescription.trim().length < 10 && (
                          <Text fontSize="xs" color="orange.600">
                            Description needs at least {10 - topicListDescription.trim().length}{" "}
                            more characters to suggest topics
                          </Text>
                        )}
                    </Field>

                    <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

                    <Field label="Reference Documents (Optional)">
                      <VStack align="stretch" gap={3}>
                        <Text fontSize="sm" color="gray.600">
                          Upload reference documents or select a Knowledge Base to help the AI
                          suggest topics.
                        </Text>

                        {/* Reference Mode Toggle */}
                        <HStack gap={2}>
                          <Button
                            size="sm"
                            variant={referenceMode === "files" ? "solid" : "outline"}
                            onClick={() => handleReferenceModeChange("files")}
                          >
                            Upload Files
                          </Button>
                          <Button
                            size="sm"
                            variant={referenceMode === "knowledge-base" ? "solid" : "outline"}
                            onClick={() => handleReferenceModeChange("knowledge-base")}
                          >
                            Knowledge Base
                          </Button>
                        </HStack>

                        {/* Reference Mode Content */}
                        {referenceMode === "files" && (
                          <VStack align="stretch" gap={2}>
                            <Text fontSize="sm" color="gray.700" fontWeight="medium">
                              Provide reference documents for suggesting topics
                            </Text>
                            <FileUpload
                              files={exampleFiles}
                              onFilesChange={setExampleFiles}
                              acceptedFileTypes={{
                                "application/pdf": [".pdf"],
                                "application/msword": [".doc"],
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                  [".docx"],
                                "text/plain": [".txt"],
                                "text/csv": [".csv"],
                                "application/json": [".json"],
                              }}
                              maxFiles={5}
                            />
                          </VStack>
                        )}

                        {referenceMode === "knowledge-base" && (
                          <Box>
                            <select
                              style={{
                                width: "100%",
                                padding: "8px",
                                borderRadius: "6px",
                                border: "1px solid #e2e8f0",
                              }}
                              value={referenceKnowledgeBase?.id || ""}
                              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                                const kb = knowledgeBases?.find((kb) => kb.id === e.target.value)
                                setReferenceKnowledgeBase(kb || null)
                              }}
                            >
                              <option value="">Select a Knowledge Base...</option>
                              {knowledgeBases?.map((kb) => (
                                <option key={kb.id} value={kb.id}>
                                  {kb.title}
                                </option>
                              ))}
                            </select>
                            {!knowledgeBases || knowledgeBases.length === 0 ? (
                              <Text fontSize="sm" color="orange.600">
                                No Knowledge Bases available. Create one first to use this feature.
                              </Text>
                            ) : null}
                          </Box>
                        )}

                        {topicListDescription.trim().length < 10 &&
                          topicListDescription.trim().length > 0 && (
                            <Text fontSize="sm" color="gray.500">
                              Description must be at least 10 characters to suggest topics
                            </Text>
                          )}
                      </VStack>
                    </Field>
                  </VStack>

                  <Field
                    label={
                      <HStack justify="space-between" w="full">
                        <span>Comparison Topics</span>
                        <HStack gap={2}>
                          <Button
                            size="xs"
                            onClick={handleSuggestTopics}
                            disabled={
                              !topicListDescription.trim() ||
                              topicListDescription.trim().length < 10 ||
                              suggesting
                            }
                            loading={suggesting}
                            variant="outline"
                            colorPalette="green"
                            title={
                              topicListDescription.trim().length < 10
                                ? "Description must be at least 10 characters to suggest topics"
                                : "Suggest topics based on the description"
                            }
                          >
                            {suggesting ? "Suggesting..." : "Suggest"}
                          </Button>

                          <IconButton
                            size="xs"
                            onClick={handleCopyTopics}
                            variant="ghost"
                            aria-label="Copy topics as text"
                            title="Copy all topics as text"
                            disabled={
                              topicsList.filter((topic) => topic.trim() !== "").length === 0
                            }
                          >
                            <FiCopy size={12} />
                          </IconButton>
                        </HStack>
                      </HStack>
                    }
                    required
                    invalid={!!validationErrors.topics}
                    errorText={validationErrors.topics}
                    py={0}
                    flex="1"
                  >
                    <VStack
                      align="stretch"
                      gap={0}
                      display="flex"
                      flexDirection="column"
                      width="100%"
                      maxH="300px"
                      overflowY="auto"
                    >
                      {topicsList.map((topic, index) => (
                        <TopicItem
                          key={index}
                          index={index}
                          topic={topic}
                          onUpdate={(idx, value) => {
                            updateTopic(idx, value)
                            // Clear validation error when topics are modified
                            if (validationErrors.topics) {
                              setValidationErrors((prev) => ({ ...prev, topics: "" }))
                            }
                          }}
                          onBlur={handleTopicBlur}
                          onRemove={removeTopic}
                          onMoveUp={moveTopicUp}
                          onMoveDown={moveTopicDown}
                          canRemove={topicsList.length > 1 && Boolean(topic && topic.trim() !== "")}
                          totalTopics={topicsList.length}
                        />
                      ))}
                    </VStack>
                  </Field>
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <HStack gap={3}>
                <CancelButton onClick={handleModalClose} size="md">
                  Cancel
                </CancelButton>
                <ConfirmButton onClick={handleSave} size="md">
                  {editingTopicList ? "Update Topic List" : "Create Topic List"}
                </ConfirmButton>
              </HStack>
            </Dialog.Footer>

            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  )
}

export default TopicListModal
