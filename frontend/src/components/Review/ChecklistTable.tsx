import { Button, Checkbox, HStack, IconButton, Table } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { FiCopy, FiEye, FiPlus, FiTrash2 } from "react-icons/fi"
import { type VeraDocChecklist, VeradocService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { generateUUID } from "../../utils/uuid"
import ChecklistModal from "./ChecklistModal"

interface QuestionData {
  id: string
  text: string
  consultDocuments: boolean
}

interface ChecklistTableProps {
  checklists: VeraDocChecklist[]
  selectedChecklist: VeraDocChecklist | null
  onChecklistChange: (checklist: VeraDocChecklist | null) => void
  onQuestionsChange: (questions: string) => void
  onStructuredQuestionsChange?: (questions: QuestionData[]) => void
  onChecklistsUpdate: () => void
  questions: string
  isDisabled?: boolean
  // New props for optimization
  knowledgeBases?: any[]
  selectedKnowledgeBase?: any
}

interface ChecklistTableHeaderProps {
  onCreateNew: () => void
}

interface ChecklistTableBodyProps {
  checklists: VeraDocChecklist[]
  selectedChecklist: VeraDocChecklist | null
  onChecklistChange: (checklist: VeraDocChecklist | null) => void
  onQuestionsChange: (questions: string) => void
  onStructuredQuestionsChange?: (questions: QuestionData[]) => void
  onViewChecklist: (checklist: VeraDocChecklist) => void
  onCopyChecklist: (checklist: VeraDocChecklist) => void
  onDeleteChecklist: (checklist: VeraDocChecklist) => void
}

const ChecklistTableHeader = ({ onCreateNew }: ChecklistTableHeaderProps) => {
  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6" />
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold" }}
        >
          Name
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold" }}
        >
          Description
        </Table.ColumnHeader>
        <Table.ColumnHeader
          w="40"
          style={{ fontSize: "0.875rem", fontWeight: "bold" }}
        >
          <HStack gap={1} ml="auto">
            <Button size="sm" onClick={onCreateNew} variant="ghost">
              <FiPlus size={14} />
            </Button>
          </HStack>
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
  onStructuredQuestionsChange,
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
          data-selected={
            selectedChecklist?.id === checklist.id ? "" : undefined
          }
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

                  // Parse and provide structured questions
                  if (onStructuredQuestionsChange) {
                    try {
                      const parsedQuestions = JSON.parse(
                        checklist.questions || "[]",
                      )
                      if (
                        Array.isArray(parsedQuestions) &&
                        parsedQuestions.every(
                          (q) =>
                            typeof q === "object" &&
                            "text" in q &&
                            "consultDocuments" in q,
                        )
                      ) {
                        // It's structured data
                        onStructuredQuestionsChange(parsedQuestions)
                      } else {
                        throw new Error("Not structured format")
                      }
                    } catch {
                      // Fallback for legacy format
                      const questionsArray = (checklist.questions || "")
                        .split("\n")
                        .filter((q) => q.trim())
                      const structuredData = questionsArray.map((text) => ({
                        id: generateUUID(),
                        text,
                        consultDocuments: true, // Default for legacy
                      }))
                      onStructuredQuestionsChange(structuredData)
                    }
                  }
                } else {
                  onChecklistChange(null)
                  onQuestionsChange("")
                  if (onStructuredQuestionsChange) {
                    onStructuredQuestionsChange([])
                  }
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
  onStructuredQuestionsChange,
  onChecklistsUpdate,
  isDisabled = false,
  knowledgeBases: _knowledgeBases = [],
  selectedKnowledgeBase = null,
}: ChecklistTableProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [checklistName, setChecklistName] = useState("")
  const [checklistDescription, setChecklistDescription] = useState("")
  const [questionsList, setQuestionsList] = useState<string[]>([])
  const [questionsData, setQuestionsData] = useState<QuestionData[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingChecklist, setEditingChecklist] =
    useState<VeraDocChecklist | null>(null)

  // Update local state when editingChecklist changes
  useEffect(() => {
    if (editingChecklist) {
      console.log("Loading checklist for editing:", editingChecklist)
      setChecklistName(editingChecklist.name || "")
      setChecklistDescription(editingChecklist.description || "")
      const checklistQuestions = editingChecklist.questions || ""
      console.log("Raw questions from database:", checklistQuestions)

      if (checklistQuestions) {
        // Try to parse as structured data first
        try {
          const parsedQuestions = JSON.parse(checklistQuestions)
          console.log("Parsed questions:", parsedQuestions)

          if (
            Array.isArray(parsedQuestions) &&
            parsedQuestions.every(
              (q) =>
                typeof q === "object" && "text" in q && "consultDocuments" in q,
            )
          ) {
            // It's structured data
            const questionsArray = parsedQuestions.map((q) => q.text)
            const structuredData = parsedQuestions.map((q) => ({
              id: q.id || generateUUID(),
              text: q.text,
              consultDocuments: q.consultDocuments,
            }))
            console.log("Setting structured data:", structuredData)
            setQuestionsList(questionsArray.length > 0 ? questionsArray : [""])
            setQuestionsData(
              structuredData.length > 0
                ? structuredData
                : [{ id: generateUUID(), text: "", consultDocuments: true }],
            )
          } else {
            throw new Error("Not structured format")
          }
        } catch {
          // Fall back to legacy string format
          const questionsArray = checklistQuestions.split("\n")
          setQuestionsList(questionsArray.length > 0 ? questionsArray : [""])
          setQuestionsData(
            questionsArray.map((text) => ({
              id: generateUUID(),
              text,
              consultDocuments: true,
            })),
          )
        }
      } else {
        setQuestionsList([""])
        setQuestionsData([
          { id: generateUUID(), text: "", consultDocuments: true },
        ])
      }
    } else {
      setChecklistName("")
      setChecklistDescription("")
      setQuestionsList([""])
      setQuestionsData([
        { id: generateUUID(), text: "", consultDocuments: true },
      ])
    }
  }, [editingChecklist])

  // Initialize with one empty question on component mount
  useEffect(() => {
    if (questionsList.length === 0) {
      setQuestionsList([""])
      setQuestionsData([
        { id: generateUUID(), text: "", consultDocuments: true },
      ])
    }
  }, [])

  // Function to sync questionsData with questionsList
  const syncQuestionsData = (newQuestionsList: string[]) => {
    const newQuestionsData = newQuestionsList.map((text, index) => ({
      id: questionsData[index]?.id || generateUUID(),
      text,
      consultDocuments: questionsData[index]?.consultDocuments ?? true,
    }))
    setQuestionsData(newQuestionsData)
  }

  // Convert questions array back to string when questionsList changes
  const updateQuestionsFromList = (newQuestionsList: string[]) => {
    setQuestionsList(newQuestionsList)
    syncQuestionsData(newQuestionsList)
  }

  // Function to update questionsData
  const updateQuestionsData = (newData: QuestionData[]) => {
    console.log("updateQuestionsData called with:", newData)
    setQuestionsData(newData)
    setQuestionsList(newData.map((q) => q.text))
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
      const newData = questionsData.filter((_, i) => i !== index)

      // Ensure we always have at least one empty question at the end
      const hasEmptyQuestion = newQuestions.some((q) => q.trim() === "")
      if (!hasEmptyQuestion) {
        newQuestions.push("")
        newData.push({ id: generateUUID(), text: "", consultDocuments: true })
      }

      setQuestionsList(newQuestions)
      setQuestionsData(newData)
    }
  }

  // Use useEffect to automatically add new questions when needed
  useEffect(() => {
    // If the last question has content and there's no empty question at the end, add one
    if (questionsList.length > 0) {
      const lastQuestion = questionsList[questionsList.length - 1]
      if (lastQuestion.trim() !== "") {
        const newQuestions = [...questionsList, ""]
        const newData = [
          ...questionsData,
          { id: generateUUID(), text: "", consultDocuments: true },
        ]
        setQuestionsList(newQuestions)
        setQuestionsData(newData)
      }
    }
  }, [questionsList])

  const removeQuestion = (index: number) => {
    // Don't allow removing if it's the only question or if it would leave no empty questions
    if (questionsList.length <= 1) return

    const newQuestions = questionsList.filter((_, i) => i !== index)
    const newData = questionsData.filter((_, i) => i !== index)

    // Ensure we always have at least one empty question at the end
    const hasEmptyQuestion = newQuestions.some((q) => q.trim() === "")
    if (
      !hasEmptyQuestion &&
      questionsList[questionsList.length - 1].trim() !== ""
    ) {
      newQuestions.push("")
      newData.push({ id: generateUUID(), text: "", consultDocuments: true })
    }

    setQuestionsList(newQuestions)
    setQuestionsData(newData)
  }

  const moveQuestionUp = (index: number) => {
    if (index === 0) return // Can't move first item up
    const newQuestions = [...questionsList]
    const newData = [...questionsData]

    // Swap questions
    const tempQuestion = newQuestions[index]
    newQuestions[index] = newQuestions[index - 1]
    newQuestions[index - 1] = tempQuestion

    // Swap data
    const tempData = newData[index]
    newData[index] = newData[index - 1]
    newData[index - 1] = tempData

    setQuestionsList(newQuestions)
    setQuestionsData(newData)
  }

  const moveQuestionDown = (index: number) => {
    if (index === questionsList.length - 1) return // Can't move last item down
    const newQuestions = [...questionsList]
    const newData = [...questionsData]

    // Swap questions
    const tempQuestion = newQuestions[index]
    newQuestions[index] = newQuestions[index + 1]
    newQuestions[index + 1] = tempQuestion

    // Swap data
    const tempData = newData[index]
    newData[index] = newData[index + 1]
    newData[index + 1] = tempData

    setQuestionsList(newQuestions)
    setQuestionsData(newData)
  }

  const handleViewChecklist = (checklist: VeraDocChecklist) => {
    setEditingChecklist(checklist)
    setIsModalOpen(true)
  }

  const handleCopyChecklist = async (checklist: VeraDocChecklist) => {
    try {
      // Generate a unique name by checking existing checklists
      const generateUniqueName = (baseName: string): string => {
        let copyName = `${baseName} (Copy)`
        let copyNumber = 1

        // Keep checking and incrementing until we find a unique name
        while (checklists.some((existing) => existing.name === copyName)) {
          copyNumber++
          copyName = `${baseName}${" (Copy)".repeat(copyNumber)}`
        }

        return copyName
      }

      const uniqueName = generateUniqueName(checklist.name || "Untitled")

      await VeradocService.createChecklist({
        requestBody: {
          name: uniqueName,
          description: checklist.description || "",
          questions: checklist.questions || "",
          owner_id: checklist.owner_id || "",
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
      // Filter out empty questions and serialize as structured JSON without IDs
      const nonEmptyQuestionsData = questionsData
        .filter((q) => q.text.trim() !== "")
        .map(({ text, consultDocuments }) => ({ text, consultDocuments }))
      const questionsJson = JSON.stringify(nonEmptyQuestionsData)

      console.log("Saving checklist with questionsData:", questionsData)
      console.log("Filtered nonEmptyQuestionsData:", nonEmptyQuestionsData)
      console.log("Final questionsJson to save:", questionsJson)

      if (editingChecklist) {
        // Update the existing checklist
        await VeradocService.updateChecklist({
          checklistId: editingChecklist.id || "",
          requestBody: {
            name: checklistName,
            description: checklistDescription,
            questions: questionsJson,
            owner_id: editingChecklist.owner_id || "",
          },
        })

        showSuccessToast("Checklist updated successfully.")
      } else {
        // Create a new checklist
        await VeradocService.createChecklist({
          requestBody: {
            name: checklistName,
            description: checklistDescription,
            questions: questionsJson,
            owner_id: "",
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
    <div
      style={{
        opacity: isDisabled ? 0.3 : 1,
        pointerEvents: isDisabled ? "none" : "auto",
      }}
    >
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
            onStructuredQuestionsChange={onStructuredQuestionsChange}
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
        questionsData={questionsData}
        updateQuestion={updateQuestion}
        updateQuestionsList={updateQuestionsFromList}
        updateQuestionsData={updateQuestionsData}
        handleQuestionBlur={handleQuestionBlur}
        removeQuestion={removeQuestion}
        moveQuestionUp={moveQuestionUp}
        moveQuestionDown={moveQuestionDown}
        knowledgeBases={_knowledgeBases}
        selectedKnowledgeBase={selectedKnowledgeBase}
      />
    </div>
  )
}

export default ChecklistTable
