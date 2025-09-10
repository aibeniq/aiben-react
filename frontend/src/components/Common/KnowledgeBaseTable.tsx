import type { KnowledgeBasePublic } from "@/client"
import { Checkbox, Table } from "@chakra-ui/react"
import { FiCheck } from "react-icons/fi"
import { useTranslation } from "react-i18next"

interface TableCardProps {
  knowledgeBases: KnowledgeBasePublic[]
  selectedKnowledgeBase: KnowledgeBasePublic | null
  onSelectionChange: (selectedKb: KnowledgeBasePublic | null) => void
  onKnowledgeBaseSelect?: (kb: KnowledgeBasePublic) => void
}

interface TableHeaderProps {
  hasSelection: boolean
}

interface TableBodyProps {
  knowledgeBases: KnowledgeBasePublic[]
  selectedId: string
  onRowSelection: (kb: KnowledgeBasePublic, isChecked: boolean) => void
}

const TableHeader = ({ hasSelection }: TableHeaderProps) => {
  const { t } = useTranslation()

  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6">
          <span style={{ fontSize: "0.875rem", fontWeight: "medium" }}>
            {hasSelection ? <FiCheck /> : ""}
          </span>
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTableName")}
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTableDescription")}
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTableSources")}
        </Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
  )
}

const TableBody = ({ knowledgeBases, selectedId, onRowSelection }: TableBodyProps) => {
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
      <Table.Cell>{kb.description || "No description"}</Table.Cell>
      <Table.Cell>{kb.number_of_sources || 0} sources</Table.Cell>
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

  const sortedKnowledgeBases = [...knowledgeBases].sort((a, b) => {
    const aSelected = selectedId === a.id
    const bSelected = selectedId === b.id

    if (aSelected !== bSelected) {
      return aSelected ? -1 : 1
    }

    return (a.title || "").localeCompare(b.title || "")
  })
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
          <TableHeader hasSelection={!!selectedId} />
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
