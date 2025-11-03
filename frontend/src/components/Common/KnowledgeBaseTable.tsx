import type { KnowledgeBasePublic } from "@/client"
import { Checkbox, Table } from "@chakra-ui/react"
import { useTranslation } from "react-i18next"
import { useState } from "react"
import { FiCheck, FiChevronUp, FiChevronDown } from "react-icons/fi"

interface TableCardProps {
  knowledgeBases: KnowledgeBasePublic[]
  selectedKnowledgeBase: KnowledgeBasePublic | null
  onSelectionChange: (selectedKb: KnowledgeBasePublic | null) => void
  onKnowledgeBaseSelect?: (kb: KnowledgeBasePublic) => void
}

interface TableHeaderProps {
  hasSelection: boolean
  sortBy: string | null
  sortOrder: "asc" | "desc"
  onSort: (column: string) => void
}

interface TableBodyProps {
  knowledgeBases: KnowledgeBasePublic[]
  selectedId: string
  onRowSelection: (kb: KnowledgeBasePublic, isChecked: boolean) => void
}

const TableHeader = ({ hasSelection, sortBy, sortOrder, onSort }: TableHeaderProps) => {
  const { t } = useTranslation()

  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6">
          <span style={{ fontSize: "0.875rem", fontWeight: "medium" }}>
            {hasSelection ? <FiCheck /> : ""}
          </span>
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold", cursor: "pointer" }}
          onClick={() => onSort("title")}
        >
          {t("chatbot.knowledgeBaseTableName")}
          {sortBy === "title" &&
            (sortOrder === "asc" ? (
              <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
            ) : (
              <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
            ))}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold", cursor: "pointer" }}
          onClick={() => onSort("description")}
        >
          {t("chatbot.knowledgeBaseTableDescription")}
          {sortBy === "description" &&
            (sortOrder === "asc" ? (
              <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
            ) : (
              <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
            ))}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold", cursor: "pointer" }}
          onClick={() => onSort("number_of_sources")}
        >
          {t("chatbot.knowledgeBaseTableSources")}
          {sortBy === "number_of_sources" &&
            (sortOrder === "asc" ? (
              <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
            ) : (
              <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
            ))}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold", cursor: "pointer" }}
          onClick={() => onSort("total_pages")}
        >
          {t("chatbot.knowledgeBaseTablePages")}
          {sortBy === "total_pages" &&
            (sortOrder === "asc" ? (
              <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
            ) : (
              <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
            ))}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold", cursor: "pointer" }}
          onClick={() => onSort("date_created")}
        >
          {t("knowledgeBases.tableHeaders.dateCreated")}
          {sortBy === "date_created" &&
            (sortOrder === "asc" ? (
              <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
            ) : (
              <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
            ))}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold", cursor: "pointer" }}
          onClick={() => onSort("date_modified")}
        >
          {t("knowledgeBases.tableHeaders.dateModified")}
          {sortBy === "date_modified" &&
            (sortOrder === "asc" ? (
              <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
            ) : (
              <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
            ))}
        </Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
  )
}

const TableBody = ({ knowledgeBases, selectedId, onRowSelection }: TableBodyProps) => {
  const { t } = useTranslation()
  const rows = knowledgeBases.map((kb) => (
    <Table.Row key={kb.id} data-selected={selectedId === kb.id ? "" : undefined}>
      <Table.Cell>
        <Checkbox.Root
          size="sm"
          top="0.5"
          aria-label="Select row"
          checked={selectedId === kb.id}
          onCheckedChange={(changes) => {
            onRowSelection(kb, !!changes.checked)
          }}
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
        </Checkbox.Root>
      </Table.Cell>
      <Table.Cell>{kb.title}</Table.Cell>
      <Table.Cell>{kb.description || t("chatbot.knowledgeBaseTable.noDescription")}</Table.Cell>
      <Table.Cell>
        {t("chatbot.knowledgeBaseTable.sourcesCount", {
          count: kb.number_of_sources || 0,
        })}
      </Table.Cell>
      <Table.Cell>
        {t("chatbot.knowledgeBaseTable.pagesCount", {
          count: kb.total_pages || 0,
        })}
      </Table.Cell>
      <Table.Cell>{new Date(kb.date_created).toLocaleDateString()}</Table.Cell>
      <Table.Cell>{new Date(kb.date_modified).toLocaleDateString()}</Table.Cell>
    </Table.Row>
  ))

  return <Table.Body>{rows}</Table.Body>
}

const KnowledgeBaseTable = ({
  knowledgeBases,
  selectedKnowledgeBase,
  onSelectionChange,
  onKnowledgeBaseSelect,
}: TableCardProps) => {
  const selectedId = selectedKnowledgeBase?.id || ""

  // Add sorting state
  const [sortBy, setSortBy] = useState<string | null>(null)
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc")

  // Sorting function
  const sortKnowledgeBases = (kbs: KnowledgeBasePublic[]) => {
    if (!sortBy) return kbs
    return [...kbs].sort((a, b) => {
      let aVal: any, bVal: any
      switch (sortBy) {
        case "title":
          aVal = (a.title || "").toLowerCase()
          bVal = (b.title || "").toLowerCase()
          break
        case "description":
          aVal = (a.description || "").toLowerCase()
          bVal = (b.description || "").toLowerCase()
          break
        case "number_of_sources":
          aVal = a.number_of_sources || 0
          bVal = b.number_of_sources || 0
          break
        case "total_pages":
          aVal = a.total_pages || 0
          bVal = b.total_pages || 0
          break
        case "date_created":
          aVal = new Date(a.date_created).getTime()
          bVal = new Date(b.date_created).getTime()
          break
        case "date_modified":
          aVal = new Date(a.date_modified).getTime()
          bVal = new Date(b.date_modified).getTime()
          break
        default:
          return 0
      }
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1
      return 0
    })
  }

  // Handle sort click
  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc")
    } else {
      setSortBy(column)
      setSortOrder("asc")
    }
  }

  const handleRowSelection = (kb: KnowledgeBasePublic, isChecked: boolean) => {
    let newSelection: KnowledgeBasePublic | null

    if (isChecked) {
      newSelection = kb
      if (onKnowledgeBaseSelect) {
        onKnowledgeBaseSelect(kb)
      }
    } else {
      newSelection = null
    }

    onSelectionChange(newSelection)
  }

  // Sort the knowledge bases
  const sortedKnowledgeBases = sortKnowledgeBases(knowledgeBases)
  return (
    <>
      <div
        style={{
          maxHeight: "300px",
          overflowY: "auto",
          border: "1px solid #E2E8F0",
          borderRadius: "8px",
          width: "100%",
        }}
      >
        <Table.Root variant="line" showColumnBorder>
          <TableHeader
            hasSelection={!!selectedId}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSort={handleSort}
          />
          <TableBody
            knowledgeBases={sortedKnowledgeBases}
            selectedId={selectedId}
            onRowSelection={handleRowSelection}
          />
        </Table.Root>
      </div>
      {/* <ActionBar hasSelection={selectedIds.length > 0} selectedIds={selectedIds} /> */}
    </>
  )
}

// const ActionBar = ({
//   hasSelection,
//   selectedIds,
// }: {
//   hasSelection: boolean
//   selectedIds: string[]
// }) => {
//   return (
//     <ActionBarChakra.Root open={hasSelection}>
//       <Portal>
//         <ActionBarChakra.Positioner>
//           <ActionBarChakra.Content>
//             <ActionBarChakra.SelectionTrigger>
//               {selectedIds.length} selected
//             </ActionBarChakra.SelectionTrigger>
//             <ActionBarChakra.Separator />
//             <Button variant="outline" size="sm">
//               Process <Kbd>⌘P</Kbd>
//             </Button>
//             <Button variant="outline" size="sm">
//               Export <Kbd>⌘E</Kbd>
//             </Button>
//           </ActionBarChakra.Content>
//         </ActionBarChakra.Positioner>
//       </Portal>
//     </ActionBarChakra.Root>
//   )
// }

export default KnowledgeBaseTable
