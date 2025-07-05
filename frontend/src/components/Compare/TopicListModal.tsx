import { useState, useEffect } from "react"
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
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { TwinCheckTopicList, TwincheckService, KnowledgeBasePublic } from "../../client"
import TopicItem from "./TopicItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import FileUpload, { FileItem } from "../Common/FileUpload"
import useCustomToast from "../../hooks/useCustomToast"
import SearchModeToggle from "../Common/SearchModeToggle"

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
  selectedKnowledgeBase?: KnowledgeBasePublic | null
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
  selectedKnowledgeBase,
  knowledgeBases,
}: TopicListModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [generating, setGenerating] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    selectedKnowledgeBase || null,
  )
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")

  // Set reference mode based on preselected knowledge base
  useEffect(() => {
    if (selectedKnowledgeBase) {
      setReferenceMode("knowledge-base")
    }
  }, [selectedKnowledgeBase])

  const handleGenerateTopics = async () => {
    if (!topicListDescription.trim()) {
      showErrorToast("Please enter a topic list description first")
      return
    }

    // Validate minimum length requirement
    if (topicListDescription.trim().length < 10) {
      showErrorToast("Please enter a more detailed description (at least 10 characters)")
      return
    }

    // Validate reference requirements if any are selected
    if (referenceMode === "files" && exampleFiles.length === 0) {
      // Files mode but no files - this is okay, just use description
    } else if (referenceMode === "knowledge-base" && !referenceKnowledgeBase) {
      showErrorToast("Please select a Knowledge Base or switch to file upload mode")
      return
    }

    setGenerating(true)

    try {
      let response

      if (referenceMode === "files" && exampleFiles.length > 0) {
        // Use the existing file upload endpoint
        const files = exampleFiles.map((item) => item.file)
        response = await TwincheckService.generateTopics({
          formData: {
            description: topicListDescription.trim(),
            comparison_type: "general",
            files: files.length > 0 ? files : undefined,
          },
        })
      } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
        // Use the new JSON endpoint with knowledge base reference
        response = await TwincheckService.generateTopicsJson({
          requestBody: {
            description: topicListDescription.trim(),
            comparison_type: "general",
            knowledge_base_id: referenceKnowledgeBase.id,
            search_mode: searchMode,
          },
        })
      } else {
        // Use the basic file upload endpoint without files
        response = await TwincheckService.generateTopics({
          formData: {
            description: topicListDescription.trim(),
            comparison_type: "general",
            search_mode: searchMode,
          },
        })
      }

      // Replace current topics with generated ones
      const generatedTopics = response.topics || []
      if (generatedTopics.length > 0) {
        // Replace the entire topics list with generated topics plus an empty topic for user input
        const newTopicsList = [...generatedTopics, ""]
        updateTopicsFromList(newTopicsList)

        let successMessage = `Generated ${generatedTopics.length} topics from description`
        if (referenceMode === "files" && exampleFiles.length > 0) {
          successMessage += ` and ${exampleFiles.length} example file(s)`
        } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
          successMessage += ` using Knowledge Base "${referenceKnowledgeBase.title}"`
        }
        successMessage += ` (${searchMode === "vector" ? "vector search" : "full document scan"})`

        showSuccessToast(successMessage)
      } else {
        showErrorToast("No topics were generated. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error generating topics:", error)
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
        showErrorToast("You need to be logged in to generate topics.")
      } else if (error.status === 404) {
        showErrorToast("Generate topics feature is not available. Please contact support.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to generate topics: ${error.message || "Unknown error"}`)
      }
    } finally {
      setGenerating(false)
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

            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                <HStack align="stretch" gap={4}>
                  <VStack align="stretch" gap={4} flex="1">
                    <Field label="Topic List Name" required>
                      <Input
                        value={topicListName}
                        onChange={(e) => setTopicListName(e.target.value)}
                        placeholder="Enter topic list name"
                      />
                    </Field>

                    <Field label="Topic List Description">
                      <Textarea
                        value={topicListDescription}
                        onChange={(e) => setTopicListDescription(e.target.value)}
                        placeholder="Enter topic list description to auto-generate topics (minimum 10 characters)..."
                        resize="vertical"
                        rows={3}
                      />
                      {topicListDescription.trim().length > 0 &&
                        topicListDescription.trim().length < 10 && (
                          <Text fontSize="xs" color="orange.600">
                            Description needs at least {10 - topicListDescription.trim().length}{" "}
                            more characters to generate topics
                          </Text>
                        )}
                    </Field>

                    <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

                    <Field label="Reference for Topic Generation (Optional)">
                      <VStack align="stretch" gap={3}>
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
                        {referenceMode === "files" ? (
                          <VStack align="stretch" gap={2}>
                            <Text fontSize="sm" color="gray.600">
                              Upload an example document to help the AI understand the desired
                              comparison scope and style.
                            </Text>
                            <FileUpload
                              files={exampleFiles}
                              onFilesChange={setExampleFiles}
                              maxFiles={1}
                              showHandwrittenToggle={false}
                            />
                          </VStack>
                        ) : (
                          <VStack align="stretch" gap={2}>
                            <Text fontSize="sm" color="gray.600">
                              Select a Knowledge Base to provide context and examples for topic
                              generation.
                            </Text>
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
                          </VStack>
                        )}
                      </VStack>
                    </Field>
                  </VStack>

                  <Field
                    label={
                      <HStack justify="space-between" w="full">
                        <span>Comparison Topics</span>
                        <Button
                          size="xs"
                          onClick={handleGenerateTopics}
                          disabled={
                            !topicListDescription.trim() ||
                            topicListDescription.trim().length < 10 ||
                            generating
                          }
                          loading={generating}
                          variant="outline"
                          colorPalette="green"
                          title={
                            topicListDescription.trim().length < 10
                              ? "Description must be at least 10 characters to generate topics"
                              : "Generate topics based on the description"
                          }
                        >
                          {generating ? "Generating..." : "Generate Topics"}
                        </Button>
                      </HStack>
                    }
                    required
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
                          onUpdate={updateTopic}
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
                <ConfirmButton onClick={onSave} size="md">
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
