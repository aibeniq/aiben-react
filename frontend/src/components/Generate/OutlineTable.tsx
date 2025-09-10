import { Button, Checkbox, HStack, IconButton, Table } from "@chakra-ui/react"
import { useState } from "react"
import { FiCopy, FiEye, FiPlus, FiTrash2 } from "react-icons/fi"
import { useTranslation } from "react-i18next"
import { type KnowledgeBasePublic, type ReportGenieOutline, ReportgenieService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { generateUUID } from "../../utils/uuid"
import OutlineModal from "./OutlineModal"

interface OutlineTableProps {
  outlines: ReportGenieOutline[]
  selectedOutline: ReportGenieOutline | null
  onOutlineChange: (outline: ReportGenieOutline | null) => void
  onSectionsChange: (sections: string) => void
  onOutlinesUpdate: () => void
  sections: string
  isDisabled?: boolean
  selectedKnowledgeBase?: KnowledgeBasePublic | null
  knowledgeBases?: KnowledgeBasePublic[]
}

interface OutlineTableHeaderProps {
  onCreateNew: () => void
}

interface OutlineTableBodyProps {
  outlines: ReportGenieOutline[]
  selectedOutline: ReportGenieOutline | null
  onOutlineChange: (outline: ReportGenieOutline | null) => void
  onSectionsChange: (sections: string) => void
  onViewOutline: (outline: ReportGenieOutline) => void
  onCopyOutline: (outline: ReportGenieOutline) => void
  onDeleteOutline: (outline: ReportGenieOutline) => void
}

const OutlineTableHeader = ({ onCreateNew }: OutlineTableHeaderProps) => {
  const { t } = useTranslation()

  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6" />
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("modelSelection.tableHeaders.name")}
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("modelSelection.tableHeaders.description")}
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

const OutlineTableBody = ({
  outlines,
  selectedOutline,
  onOutlineChange,
  onSectionsChange,
  onViewOutline,
  onCopyOutline,
  onDeleteOutline,
}: OutlineTableBodyProps) => {
  const handleRowSelection = (outline: ReportGenieOutline, isChecked: boolean) => {
    if (isChecked) {
      onOutlineChange(outline)
      onSectionsChange(outline.sections || "")
    } else {
      onOutlineChange(null)
      onSectionsChange("")
    }
  }

  // Sort outlines: selected first, then alphabetically
  const sortedOutlines = [...outlines].sort((a, b) => {
    const aSelected = selectedOutline?.id === a.id
    const bSelected = selectedOutline?.id === b.id

    if (aSelected !== bSelected) {
      return aSelected ? -1 : 1
    }

    return (a.name || "").localeCompare(b.name || "")
  })

  return (
    <Table.Body>
      {sortedOutlines.map((outline) => (
        <Table.Row
          key={outline.id}
          data-selected={selectedOutline?.id === outline.id ? "" : undefined}
        >
          <Table.Cell>
            <Checkbox.Root
              size="sm"
              top="0.5"
              aria-label="Select row"
              checked={selectedOutline?.id === outline.id}
              onCheckedChange={(details) => {
                handleRowSelection(outline, !!details.checked)
              }}
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
            </Checkbox.Root>
          </Table.Cell>
          <Table.Cell>{outline.name}</Table.Cell>
          <Table.Cell>{outline.description || ""}</Table.Cell>
          <Table.Cell>
            <HStack gap={1} justify="center">
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="View outline"
                onClick={() => onViewOutline(outline)}
              >
                <FiEye size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="Copy outline"
                onClick={() => onCopyOutline(outline)}
              >
                <FiCopy size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                colorPalette="red"
                aria-label="Delete outline"
                onClick={() => onDeleteOutline(outline)}
              >
                <FiTrash2 size={14} />
              </IconButton>
            </HStack>
          </Table.Cell>
        </Table.Row>
      ))}
      {outlines.length === 0 && (
        <Table.Row>
          <Table.Cell colSpan={4} textAlign="center" py={8} color="gray.500">
            No outlines available. Create your first outline to get started.
          </Table.Cell>
        </Table.Row>
      )}
    </Table.Body>
  )
}

const OutlineTable = ({
  outlines,
  selectedOutline,
  onOutlineChange,
  onSectionsChange,
  onOutlinesUpdate,
  sections,
  isDisabled = false,
  selectedKnowledgeBase,
  knowledgeBases,
}: OutlineTableProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingOutline, setEditingOutline] = useState<ReportGenieOutline | null>(null)
  const [outlineName, setOutlineName] = useState("")
  const [outlineDescription, setOutlineDescription] = useState("")

  const handleViewOutline = (outline: ReportGenieOutline) => {
    console.log("🔍 OutlineTable: Opening edit modal for outline:", outline.name)
    console.log("🔍 OutlineTable: Raw outline.sections:", outline.sections)
    console.log("🔍 OutlineTable: Type of outline.sections:", typeof outline.sections)

    setEditingOutline(outline)
    setOutlineName(outline.name)
    setOutlineDescription(outline.description || "")

    // Ensure sections is always passed as a properly stringified JSON
    let sectionsString = ""
    if (outline.sections) {
      if (typeof outline.sections === "string") {
        // If it's already a string, verify it's valid JSON, otherwise use as-is
        try {
          const parsed = JSON.parse(outline.sections)
          console.log("🔍 OutlineTable: Successfully parsed sections JSON:", parsed)
          sectionsString = outline.sections
        } catch (error) {
          console.log(
            "🔍 OutlineTable: Failed to parse sections as JSON, treating as plain text:",
            error,
          )
          // If parsing fails, treat as plain text and convert to structured format
          sectionsString = JSON.stringify([
            {
              id: generateUUID(),
              text: outline.sections,
              consultDocuments: true,
            },
          ])
        }
      } else if (Array.isArray(outline.sections)) {
        console.log("🔍 OutlineTable: Sections is array, stringifying:", outline.sections)
        // If it's already parsed as an array, stringify it
        sectionsString = JSON.stringify(outline.sections)
      } else {
        console.log(
          "🔍 OutlineTable: Sections is unknown format, using empty string:",
          outline.sections,
        )
        // Fallback for any other format
        sectionsString = ""
      }
    } else {
      console.log("🔍 OutlineTable: No sections found in outline")
    }

    console.log("🔍 OutlineTable: Final sectionsString being passed:", sectionsString)
    onSectionsChange(sectionsString)
    setIsModalOpen(true)
  }

  const handleCopyOutline = async (outline: ReportGenieOutline) => {
    try {
      await ReportgenieService.createOutline({
        requestBody: {
          name: `${outline.name} (Copy)`,
          description: outline.description || "",
          sections: outline.sections,
          owner_id: outline.owner_id || "",
        },
      })
      showSuccessToast("Outline copied successfully")
      onOutlinesUpdate()
    } catch (error) {
      console.error("Error copying outline:", error)
      showErrorToast("Failed to copy outline")
    }
  }

  const handleDeleteOutline = async (outline: ReportGenieOutline) => {
    try {
      await ReportgenieService.deleteOutline({ outlineId: outline.id || "" })
      showSuccessToast("Outline deleted successfully")
      if (selectedOutline?.id === outline.id) {
        onOutlineChange(null)
        onSectionsChange("")
      }
      onOutlinesUpdate()
    } catch (error) {
      console.error("Error deleting outline:", error)
      showErrorToast("Failed to delete outline")
    }
  }

  const handleCreateNew = () => {
    setEditingOutline(null)
    setOutlineName("")
    setOutlineDescription("")
    // Initialize with an empty section for immediate editing
    onSectionsChange(JSON.stringify([{ id: generateUUID(), text: "", consultDocuments: true }]))
    setIsModalOpen(true)
  }

  const handleSaveOutline = async () => {
    if (!outlineName.trim()) {
      showErrorToast("Please enter a name for this outline")
      return
    }

    if (!sections.trim()) {
      showErrorToast("Please enter at least one section")
      return
    }

    try {
      if (editingOutline) {
        await ReportgenieService.updateOutline({
          outlineId: editingOutline.id || "",
          requestBody: {
            name: outlineName,
            description: outlineDescription,
            sections: sections,
            owner_id: editingOutline.owner_id || "",
          },
        })
        showSuccessToast("Outline updated successfully")
      } else {
        await ReportgenieService.createOutline({
          requestBody: {
            name: outlineName,
            description: outlineDescription,
            sections: sections,
            owner_id: "", // This will be set by the backend
          },
        })
        showSuccessToast("Outline created successfully")
      }

      setIsModalOpen(false)
      setEditingOutline(null)
      setOutlineName("")
      setOutlineDescription("")
      onOutlinesUpdate()
    } catch (error: any) {
      console.error("Error saving outline:", error)
      showErrorToast(`Failed to save outline: ${error.message || "Unknown error"}`)
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingOutline(null)
    // Clear sections when closing modal to prevent stale state
    onSectionsChange("")
  }

  return (
    <div
      style={{
        opacity: isDisabled ? 0.3 : 1,
        pointerEvents: isDisabled ? "none" : "auto",
      }}
    >
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
          <OutlineTableHeader onCreateNew={handleCreateNew} />
          <OutlineTableBody
            outlines={outlines}
            selectedOutline={selectedOutline}
            onOutlineChange={onOutlineChange}
            onSectionsChange={onSectionsChange}
            onViewOutline={handleViewOutline}
            onCopyOutline={handleCopyOutline}
            onDeleteOutline={handleDeleteOutline}
          />
        </Table.Root>
      </div>

      <OutlineModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        editingOutline={editingOutline}
        onSave={handleSaveOutline}
        outlineName={outlineName}
        setOutlineName={setOutlineName}
        outlineDescription={outlineDescription}
        setOutlineDescription={setOutlineDescription}
        sections={sections}
        onSectionsChange={onSectionsChange}
        selectedKnowledgeBase={selectedKnowledgeBase}
        knowledgeBases={knowledgeBases}
      />
    </div>
  )
}

export default OutlineTable
