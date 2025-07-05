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
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { TwinCheckTopicList, TwincheckService } from "../../client"
import TopicItem from "./TopicItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import FileUpload, { FileItem } from "../Common/FileUpload"
import useCustomToast from "../../hooks/useCustomToast"

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
  handleTopicBlur: (index: number, value: string) => void
  removeTopic: (index: number) => void
  moveTopicUp: (index: number) => void
  moveTopicDown: (index: number) => void
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
  handleTopicBlur,
  removeTopic,
  moveTopicUp,
  moveTopicDown,
}: TopicListModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [generating, setGenerating] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])

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

    setGenerating(true)

    try {
      // Extract files from FileItem objects for the API call
      const files = exampleFiles.map((item) => item.file)

      const response = await TwincheckService.generateTopics({
        formData: {
          description: topicListDescription.trim(),
          comparison_type: "general",
          files: files.length > 0 ? files : undefined,
        },
      })

      // Replace current topics with generated ones
      const generatedTopics = response.topics || []
      if (generatedTopics.length > 0) {
        // Update topics through the parent component's state management
        // We'll call updateTopic for each generated topic
        generatedTopics.forEach((topic: string, index: number) => {
          updateTopic(index, topic)
        })

        // Add empty topic at the end if needed
        if (topicsList.length <= generatedTopics.length) {
          updateTopic(generatedTopics.length, "")
        }

        showSuccessToast(`Generated ${generatedTopics.length} topics from description`)
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

                    <Field label="Example Document (Optional)">
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
                          canRemove={topicsList.length > 1 && topic.trim() !== ""}
                          totalTopics={topicsList.length}
                        />
                      ))}
                    </VStack>
                  </Field>
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <CancelButton onClick={handleModalClose} size="md">
                  Cancel
                </CancelButton>
              </Dialog.ActionTrigger>
              <ConfirmButton onClick={onSave} size="md">
                {editingTopicList ? "Update Topic List" : "Create Topic List"}
              </ConfirmButton>
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
