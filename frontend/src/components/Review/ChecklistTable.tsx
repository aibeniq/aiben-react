import { useState, useEffect } from "react"
import { Button, HStack, IconButton, Table, Checkbox } from "@chakra-ui/react"
import { FiEye, FiCopy, FiTrash2, FiPlus } from "react-icons/fi"
import { VeraDocChecklist, VeradocService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import ChecklistModal from "./ChecklistModal"

interface ChecklistTableProps {
  checklists: VeraDocChecklist[]
  selectedChecklist: VeraDocChecklist | null
  onChecklistChange: (checklist: VeraDocChecklist | null) => void
  onQuestionsChange: (questions: string) => void
  onChecklistsUpdate: () => void
  questions: string
  isDisabled?: boolean
}

interface ChecklistTableHeaderProps {
  onCreateNew: () => void
}

interface ChecklistTableBodyProps {
  checklists: VeraDocChecklist[]
  selectedChecklist: VeraDocChecklist | null
  onChecklistChange: (checklist: VeraDocChecklist | null) => void
  onQuestionsChange: (questions: string) => void
  onViewChecklist: (checklist: VeraDocChecklist) => void
  onCopyChecklist: (checklist: VeraDocChecklist) => void
  onDeleteChecklist: (checklist: VeraDocChecklist) => void
}

const ChecklistTableHeader = ({ onCreateNew }: ChecklistTableHeaderProps) => {
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

const ChecklistTableBody = ({
  checklists,
  selectedChecklist,
  onChecklistChange,
  onQuestionsChange,
  onViewChecklist,
  onCopyChecklist,
  onDeleteChecklist,
}: ChecklistTableBodyProps) => {
  // Sort checklists: selected first, then alphabetically
  const sortedChecklists = [...checklists].sort((a, b) => {
    const aSelected = selectedChecklist?.id === a.id
    const bSelected = selectedChecklist?.id === b.id

    if (aSelected !== bSelected) {
      return aSelected ? -1 : 1
    }

    return (a.name || "").localeCompare(b.name || "")
  })

  return (
    <Table.Body>
      {sortedChecklists.map((checklist) => (
        <Table.Row
          key={checklist.id}
          data-selected={selectedChecklist?.id === checklist.id ? "" : undefined}
        >
          <Table.Cell>
            <Checkbox.Root
              size="sm"
              top="0.5"
              aria-label="Select row"
              checked={selectedChecklist?.id === checklist.id}
              onCheckedChange={(details) => {
                if (details.checked) {
                  onChecklistChange(checklist)
                  onQuestionsChange(checklist.questions || "")
                } else {
                  onChecklistChange(null)
                  onQuestionsChange("")
                }
              }}
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
            </Checkbox.Root>
          </Table.Cell>
          <Table.Cell>{checklist.name}</Table.Cell>
          <Table.Cell>{checklist.description || ""}</Table.Cell>
          <Table.Cell>
            <HStack gap={1} justify="center">
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="View checklist"
                onClick={() => onViewChecklist(checklist)}
              >
                <FiEye size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="Copy checklist"
                onClick={() => onCopyChecklist(checklist)}
              >
                <FiCopy size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                colorPalette="red"
                aria-label="Delete checklist"
                onClick={() => onDeleteChecklist(checklist)}
              >
                <FiTrash2 size={14} />
              </IconButton>
            </HStack>
          </Table.Cell>
        </Table.Row>
      ))}
      {checklists.length === 0 && (
        <Table.Row>
          <Table.Cell colSpan={4} textAlign="center" py={8} color="gray.500">
            No checklists available. Create your first checklist to get started.
          </Table.Cell>
        </Table.Row>
      )}
    </Table.Body>
  )
}

const ChecklistTable = ({
  checklists,
  selectedChecklist,
  onChecklistChange,
  onQuestionsChange,
  onChecklistsUpdate,
  isDisabled = false,
}: ChecklistTableProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [checklistName, setChecklistName] = useState("")
  const [checklistDescription, setChecklistDescription] = useState("")
  const [questionsList, setQuestionsList] = useState<string[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingChecklist, setEditingChecklist] = useState<VeraDocChecklist | null>(null)

  // Update local state when editingChecklist changes
  useEffect(() => {
    if (editingChecklist) {
      setChecklistName(editingChecklist.name || "")
      setChecklistDescription(editingChecklist.description || "")
      const checklistQuestions = editingChecklist.questions || ""
      if (checklistQuestions) {
        const questionsArray = checklistQuestions.split("\n")
        setQuestionsList(questionsArray.length > 0 ? questionsArray : [""])
      } else {
        setQuestionsList([""])
      }
    } else {
      setChecklistName("")
      setChecklistDescription("")
      setQuestionsList([""])
    }
  }, [editingChecklist])

  // Initialize with one empty question on component mount
  useEffect(() => {
    if (questionsList.length === 0) {
      setQuestionsList([""])
    }
  }, [])

  // Convert questions array back to string when questionsList changes
  const updateQuestionsFromList = (newQuestionsList: string[]) => {
    setQuestionsList(newQuestionsList)
  }

  const updateQuestion = (index: number, value: string) => {
    const newQuestions = [...questionsList]
    newQuestions[index] = value
    updateQuestionsFromList(newQuestions)
  }

  const handleQuestionBlur = (index: number, value: string) => {
    // If the question is empty and it's not the only question, remove it
    if (value.trim() === "" && questionsList.length > 1) {
      const newQuestions = questionsList.filter((_, i) => i !== index)

      // Ensure we always have at least one empty question at the end
      const hasEmptyQuestion = newQuestions.some((q) => q.trim() === "")
      if (!hasEmptyQuestion) {
        newQuestions.push("")
      }

      updateQuestionsFromList(newQuestions)
    }
  }

  // Use useEffect to automatically add new questions when needed
  useEffect(() => {
    // If the last question has content and there's no empty question at the end, add one
    if (questionsList.length > 0) {
      const lastQuestion = questionsList[questionsList.length - 1]
      if (lastQuestion.trim() !== "") {
        updateQuestionsFromList([...questionsList, ""])
      }
    }
  }, [questionsList])

  const removeQuestion = (index: number) => {
    // Don't allow removing if it's the only question or if it would leave no empty questions
    if (questionsList.length <= 1) return

    const newQuestions = questionsList.filter((_, i) => i !== index)

    // Ensure we always have at least one empty question at the end
    const hasEmptyQuestion = newQuestions.some((q) => q.trim() === "")
    if (!hasEmptyQuestion && questionsList[questionsList.length - 1].trim() !== "") {
      newQuestions.push("")
    }

    updateQuestionsFromList(newQuestions)
  }

  const moveQuestionUp = (index: number) => {
    if (index === 0) return // Can't move first item up
    const newQuestions = [...questionsList]
    const temp = newQuestions[index]
    newQuestions[index] = newQuestions[index - 1]
    newQuestions[index - 1] = temp
    updateQuestionsFromList(newQuestions)
  }

  const moveQuestionDown = (index: number) => {
    if (index === questionsList.length - 1) return // Can't move last item down
    const newQuestions = [...questionsList]
    const temp = newQuestions[index]
    newQuestions[index] = newQuestions[index + 1]
    newQuestions[index + 1] = temp
    updateQuestionsFromList(newQuestions)
  }

  const handleViewChecklist = (checklist: VeraDocChecklist) => {
    setEditingChecklist(checklist)
    setIsModalOpen(true)
  }

  const handleCopyChecklist = async (checklist: VeraDocChecklist) => {
    try {
      await VeradocService.createChecklist({
        requestBody: {
          name: `${checklist.name} (Copy)`,
          description: checklist.description || "",
          questions: checklist.questions || "",
        },
      })

      showSuccessToast("Checklist copied successfully.")
      onChecklistsUpdate()
    } catch (error) {
      console.error("Error copying checklist:", error)
      showErrorToast("Failed to copy checklist. Please try again.")
    }
  }

  const handleDeleteChecklist = async (checklist: VeraDocChecklist) => {
    try {
      // Call the deleteChecklist method from VeradocService
      await VeradocService.deleteChecklist({ checklistId: checklist.id || "" })

      // Clear the selected checklist if it was the one being deleted
      if (selectedChecklist?.id === checklist.id) {
        onChecklistChange(null)
        onQuestionsChange("")
      }

      showSuccessToast("Checklist deleted successfully.")
      onChecklistsUpdate()
    } catch (error) {
      console.error("Error deleting checklist:", error)
      showErrorToast("Failed to delete checklist. Please try again.")
    }
  }

  const handleSaveChecklist = async () => {
    try {
      const questionsString = questionsList.join("\n")

      if (editingChecklist) {
        const trimmedQuestions = questionsString.trim()
        // Update the existing checklist
        await VeradocService.updateChecklist({
          checklistId: editingChecklist.id || "",
          requestBody: {
            name: checklistName,
            description: checklistDescription,
            questions: trimmedQuestions,
          },
        })

        showSuccessToast("Checklist updated successfully.")
      } else {
        // Create a new checklist
        await VeradocService.createChecklist({
          requestBody: {
            name: checklistName,
            description: checklistDescription,
            questions: questionsString,
          },
        })

        showSuccessToast("Checklist created successfully.")
      }

      // Close modal and refresh
      setIsModalOpen(false)
      setEditingChecklist(null)
      onChecklistsUpdate()
    } catch (error) {
      console.error("Error saving checklist:", error)
      showErrorToast("Failed to save checklist. Please try again.")
    }
  }

  const handleCreateNew = () => {
    setEditingChecklist(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingChecklist(null)
  }

  return (
    <div style={{ opacity: isDisabled ? 0.3 : 1, pointerEvents: isDisabled ? "none" : "auto" }}>
      {/* Checklist Table */}
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
          <ChecklistTableHeader onCreateNew={handleCreateNew} />
          <ChecklistTableBody
            checklists={checklists}
            selectedChecklist={selectedChecklist}
            onChecklistChange={onChecklistChange}
            onQuestionsChange={onQuestionsChange}
            onViewChecklist={handleViewChecklist}
            onCopyChecklist={handleCopyChecklist}
            onDeleteChecklist={handleDeleteChecklist}
          />
        </Table.Root>
      </div>

      {/* Checklist Editor Modal */}
      <ChecklistModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        editingChecklist={editingChecklist}
        onSave={handleSaveChecklist}
        checklistName={checklistName}
        setChecklistName={setChecklistName}
        checklistDescription={checklistDescription}
        setChecklistDescription={setChecklistDescription}
        questionsList={questionsList}
        updateQuestion={updateQuestion}
        handleQuestionBlur={handleQuestionBlur}
        removeQuestion={removeQuestion}
        moveQuestionUp={moveQuestionUp}
        moveQuestionDown={moveQuestionDown}
      />
    </div>
  )
}

export default ChecklistTable
