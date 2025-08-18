import { useState, useEffect } from "react"
import { Button, HStack, IconButton, Table, Checkbox } from "@chakra-ui/react"
import { FiEye, FiCopy, FiTrash2, FiPlus } from "react-icons/fi"
import { TwinCheckTopicList, TwincheckService, KnowledgeBasePublic } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import TopicListModal from "./TopicListModal"

interface TopicListTableProps {
  topicLists: TwinCheckTopicList[]
  selectedTopicList: TwinCheckTopicList | null
  onTopicListChange: (topicList: TwinCheckTopicList | null) => void
  onTopicsChange: (topics: string) => void
  onTopicListsUpdate: () => void
  topics: string
  isDisabled?: boolean
  knowledgeBases?: KnowledgeBasePublic[]
}

interface TopicListTableHeaderProps {
  onCreateNew: () => void
}

interface TopicListTableBodyProps {
  topicLists: TwinCheckTopicList[]
  selectedTopicList: TwinCheckTopicList | null
  onTopicListChange: (topicList: TwinCheckTopicList | null) => void
  onTopicsChange: (topics: string) => void
  onViewTopicList: (topicList: TwinCheckTopicList) => void
  onCopyTopicList: (topicList: TwinCheckTopicList) => void
  onDeleteTopicList: (topicList: TwinCheckTopicList) => void
}

const TopicListTableHeader = ({ onCreateNew }: TopicListTableHeaderProps) => {
  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6"></Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          Name
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          Description
        </Table.ColumnHeader>
        <Table.ColumnHeader w="32" style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          <Button size="sm" onClick={onCreateNew} ml="auto" variant="ghost">
            <FiPlus size={14} />
          </Button>
        </Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
  )
}

const TopicListTableBody = ({
  topicLists,
  selectedTopicList,
  onTopicListChange,
  onTopicsChange,
  onViewTopicList,
  onCopyTopicList,
  onDeleteTopicList,
}: TopicListTableBodyProps) => {
  // Sort topic lists: selected first, then alphabetically
  const sortedTopicLists = [...topicLists].sort((a, b) => {
    const aSelected = selectedTopicList?.id === a.id
    const bSelected = selectedTopicList?.id === b.id

    if (aSelected !== bSelected) {
      return aSelected ? -1 : 1
    }

    return (a.name || "").localeCompare(b.name || "")
  })

  return (
    <Table.Body>
      {sortedTopicLists.map((topicList) => (
        <Table.Row
          key={topicList.id}
          data-selected={selectedTopicList?.id === topicList.id ? "" : undefined}
        >
          <Table.Cell>
            <Checkbox.Root
              size="sm"
              top="0.5"
              aria-label="Select row"
              checked={selectedTopicList?.id === topicList.id}
              onCheckedChange={(details) => {
                if (details.checked) {
                  onTopicListChange(topicList)
                  onTopicsChange(topicList.topics || "")
                } else {
                  onTopicListChange(null)
                  onTopicsChange("")
                }
              }}
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
            </Checkbox.Root>
          </Table.Cell>
          <Table.Cell>{topicList.name}</Table.Cell>
          <Table.Cell>{topicList.description || ""}</Table.Cell>
          <Table.Cell>
            <HStack gap={1} justify="center">
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="View topic list"
                onClick={() => onViewTopicList(topicList)}
              >
                <FiEye size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="Copy topic list"
                onClick={() => onCopyTopicList(topicList)}
              >
                <FiCopy size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                colorPalette="red"
                aria-label="Delete topic list"
                onClick={() => onDeleteTopicList(topicList)}
              >
                <FiTrash2 size={14} />
              </IconButton>
            </HStack>
          </Table.Cell>
        </Table.Row>
      ))}
      {topicLists.length === 0 && (
        <Table.Row>
          <Table.Cell colSpan={4} textAlign="center" py={8} color="gray.500">
            No topic lists available. Create your first topic list to get started.
          </Table.Cell>
        </Table.Row>
      )}
    </Table.Body>
  )
}

const TopicListTable = ({
  topicLists,
  selectedTopicList,
  onTopicListChange,
  onTopicsChange,
  onTopicListsUpdate,
  isDisabled = false,
  knowledgeBases = [],
}: TopicListTableProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [topicListName, setTopicListName] = useState("")
  const [topicListDescription, setTopicListDescription] = useState("")
  const [topicsList, setTopicsList] = useState<string[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingTopicList, setEditingTopicList] = useState<TwinCheckTopicList | null>(null)

  // Update local state when editingTopicList changes
  useEffect(() => {
    if (editingTopicList) {
      setTopicListName(editingTopicList.name || "")
      setTopicListDescription(editingTopicList.description || "")
      const topicListTopics = editingTopicList.topics || ""
      if (topicListTopics) {
        const topicsArray = topicListTopics.split("\n")
        setTopicsList(topicsArray.length > 0 ? topicsArray : [""])
      } else {
        setTopicsList([""])
      }
    } else {
      setTopicListName("")
      setTopicListDescription("")
      setTopicsList([""])
    }
  }, [editingTopicList])

  // Initialize with one empty topic on component mount
  useEffect(() => {
    if (topicsList.length === 0) {
      setTopicsList([""])
    }
  }, [])

  // Convert topics array back to string when topicsList changes
  const updateTopicsFromList = (newTopicsList: string[]) => {
    setTopicsList(newTopicsList)
  }

  const updateTopic = (index: number, value: string) => {
    const newTopics = [...topicsList]
    newTopics[index] = value
    updateTopicsFromList(newTopics)
  }

  const handleTopicBlur = (index: number, value: string) => {
    // If the topic is empty and it's not the only topic, remove it
    if (value.trim() === "" && topicsList.length > 1) {
      const newTopics = topicsList.filter((_, i) => i !== index)

      // Ensure we always have at least one empty topic at the end
      const hasEmptyTopic = newTopics.some((q) => q.trim() === "")
      if (!hasEmptyTopic) {
        newTopics.push("")
      }

      updateTopicsFromList(newTopics)
    }
  }

  // Use useEffect to automatically add new topics when needed
  useEffect(() => {
    // If the last topic has content and there's no empty topic at the end, add one
    if (topicsList.length > 0) {
      const lastTopic = topicsList[topicsList.length - 1]
      if (lastTopic.trim() !== "") {
        updateTopicsFromList([...topicsList, ""])
      }
    }
  }, [topicsList])

  const removeTopic = (index: number) => {
    // Don't allow removing if it's the only topic or if it would leave no empty topics
    if (topicsList.length <= 1) return

    const newTopics = topicsList.filter((_, i) => i !== index)

    // Ensure we always have at least one empty topic at the end
    const hasEmptyTopic = newTopics.some((q) => q.trim() === "")
    if (!hasEmptyTopic && topicsList[topicsList.length - 1].trim() !== "") {
      newTopics.push("")
    }

    updateTopicsFromList(newTopics)
  }

  const moveTopicUp = (index: number) => {
    if (index === 0) return // Can't move first item up
    const newTopics = [...topicsList]
    const temp = newTopics[index]
    newTopics[index] = newTopics[index - 1]
    newTopics[index - 1] = temp
    updateTopicsFromList(newTopics)
  }

  const moveTopicDown = (index: number) => {
    if (index === topicsList.length - 1) return // Can't move last item down
    const newTopics = [...topicsList]
    const temp = newTopics[index]
    newTopics[index] = newTopics[index + 1]
    newTopics[index + 1] = temp
    updateTopicsFromList(newTopics)
  }

  const handleViewTopicList = (topicList: TwinCheckTopicList) => {
    setEditingTopicList(topicList)
    setIsModalOpen(true)
  }

  const handleCopyTopicList = async (topicList: TwinCheckTopicList) => {
    try {
      console.log("🐛 DEBUG: Copying topic list:", topicList)
      
      // Validate the topic list data before copying
      if (!topicList.topics || !topicList.topics.trim()) {
        showErrorToast("Cannot copy topic list: no topics found")
        return
      }

      await TwincheckService.createComparison({
        requestBody: {
          name: `${topicList.name} (Copy)`.trim(),
          description: (topicList.description || "").trim(),
          topics: topicList.topics.trim(),
          owner_id: topicList.owner_id || "",
        },
      })

      showSuccessToast("Topic list copied successfully.")
      onTopicListsUpdate()
    } catch (error: any) {
      console.error("Error copying topic list:", error)
      console.error("Error details:", {
        message: error.message,
        status: error.status,
        body: error.body
      })
      
      const errorMessage = error.body?.detail || error.message || "Unknown error occurred"
      showErrorToast(`Error copying topic list: ${errorMessage}`)
    }
  }

  const handleDeleteTopicList = async (topicList: TwinCheckTopicList) => {
    try {
      // Call the deleteComparison method from TwincheckService
      await TwincheckService.deleteComparison({ comparisonId: topicList.id || "" })

      // Clear the selected topic list if it was the one being deleted
      if (selectedTopicList?.id === topicList.id) {
        onTopicListChange(null)
        onTopicsChange("")
      }

      showSuccessToast("Topic list deleted successfully.")
      onTopicListsUpdate()
    } catch (error) {
      console.error("Error deleting topic list:", error)
      showErrorToast("Failed to delete topic list. Please try again.")
    }
  }

  const handleSaveTopicList = async () => {
    try {
      // Filter out empty topics and create topics string
      const validTopics = topicsList.filter(topic => topic.trim() !== "")
      const topicsString = validTopics.join("\n")

      console.log("🐛 DEBUG: Saving topic list with data:", {
        name: topicListName,
        description: topicListDescription,
        topics: topicsString,
        validTopicsCount: validTopics.length
      })

      // Enhanced validation
      if (!topicListName.trim()) {
        showErrorToast("Topic list name is required")
        return
      }

      // Description is optional - no validation required

      if (validTopics.length === 0) {
        showErrorToast("At least one non-empty topic is required")
        return
      }

      if (editingTopicList) {
        const trimmedTopics = topicsString.trim()
        // Update the existing topic list
        await TwincheckService.updateComparison({
          comparisonId: editingTopicList.id || "",
          requestBody: {
            name: topicListName.trim(),
            description: topicListDescription.trim(),
            topics: trimmedTopics,
            owner_id: editingTopicList.owner_id || "",
          },
        })

        showSuccessToast("Topic list updated successfully.")
      } else {
        // Create a new topic list
        await TwincheckService.createComparison({
          requestBody: {
            name: topicListName.trim(),
            description: topicListDescription.trim(),
            topics: topicsString.trim(),
            owner_id: "", // This will be set by the backend
          },
        })

        showSuccessToast("Topic list created successfully.")
      }

      // Close modal and refresh
      setIsModalOpen(false)
      setEditingTopicList(null)
      onTopicListsUpdate()
    } catch (error: any) {
      console.error("Error saving topic list:", error)
      console.error("Error details:", {
        message: error.message,
        status: error.status,
        body: error.body
      })
      
      // Show specific error message from backend if available
      const errorMessage = error.body?.detail || error.message || "Unknown error occurred"
      showErrorToast(`Error saving topic list: ${errorMessage}`)
    }
  }

  const handleCreateNew = () => {
    setEditingTopicList(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTopicList(null)
  }

  return (
    <div style={{ opacity: isDisabled ? 0.3 : 1, pointerEvents: isDisabled ? "none" : "auto" }}>
      {/* Topic List Table */}
      <div
        style={{
          maxHeight: "300px",
          overflowY: "auto",
          border: "1px solid #E2E8F0",
          borderRadius: "8px",
          width: "100%",
        }}
      >
        <Table.Root variant="line">
          <TopicListTableHeader onCreateNew={handleCreateNew} />
          <TopicListTableBody
            topicLists={topicLists}
            selectedTopicList={selectedTopicList}
            onTopicListChange={onTopicListChange}
            onTopicsChange={onTopicsChange}
            onViewTopicList={handleViewTopicList}
            onCopyTopicList={handleCopyTopicList}
            onDeleteTopicList={handleDeleteTopicList}
          />
        </Table.Root>
      </div>

      {/* Topic List Editor Modal */}
      <TopicListModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        editingTopicList={editingTopicList}
        onSave={handleSaveTopicList}
        topicListName={topicListName}
        setTopicListName={setTopicListName}
        topicListDescription={topicListDescription}
        setTopicListDescription={setTopicListDescription}
        topicsList={topicsList}
        updateTopic={updateTopic}
        updateTopicsFromList={updateTopicsFromList}
        handleTopicBlur={handleTopicBlur}
        removeTopic={removeTopic}
        moveTopicUp={moveTopicUp}
        moveTopicDown={moveTopicDown}
        knowledgeBases={knowledgeBases}
      />
    </div>
  )
}

export default TopicListTable
