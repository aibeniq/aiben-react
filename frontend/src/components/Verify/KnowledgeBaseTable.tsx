import {
  ActionBar as ActionBarChakra,
  Button,
  Checkbox,
  Kbd,
  Portal,
  Table,
} from "@chakra-ui/react"
import { KnowledgeBasePublic } from "@/client"

interface TableCardProps {
  knowledgeBases: KnowledgeBasePublic[]
  selectedKnowledgeBases: KnowledgeBasePublic[]
  onSelectionChange: (selectedKbs: KnowledgeBasePublic[]) => void
  onKnowledgeBaseSelect?: (kb: KnowledgeBasePublic) => void
}

interface TableHeaderProps {
  selectedCount: number
  totalCount: number
}

interface TableBodyProps {
  knowledgeBases: KnowledgeBasePublic[]
  selectedIds: string[]
  onRowSelection: (kb: KnowledgeBasePublic, isChecked: boolean) => void
}

const TableHeader = ({ selectedCount, totalCount }: TableHeaderProps) => {
  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6">
          <span style={{ fontSize: "0.875rem", fontWeight: "medium" }}>
            {selectedCount}/{totalCount}
          </span>
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          Name
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          Description
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          Sources
        </Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
  )
}

const TableBody = ({ knowledgeBases, selectedIds, onRowSelection }: TableBodyProps) => {
  const rows = knowledgeBases.map((kb) => (
    <Table.Row key={kb.id} data-selected={selectedIds.includes(kb.id) ? "" : undefined}>
      <Table.Cell>
        <Checkbox.Root
          size="sm"
          top="0.5"
          aria-label="Select row"
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
  selectedKnowledgeBases,
  onSelectionChange,
  onKnowledgeBaseSelect,
}: TableCardProps) => {
  const selectedIds = selectedKnowledgeBases.map((kb) => kb.id)

  const handleRowSelection = (kb: KnowledgeBasePublic, isChecked: boolean) => {
    let newSelection: KnowledgeBasePublic[]

    if (isChecked) {
      newSelection = [...selectedKnowledgeBases, kb]
      if (onKnowledgeBaseSelect) {
        onKnowledgeBaseSelect(kb)
      }
    } else {
      newSelection = selectedKnowledgeBases.filter((selected) => selected.id !== kb.id)
    }

    onSelectionChange(newSelection)
  }

  const sortedKnowledgeBases = [...knowledgeBases].sort((a, b) => {
    const aSelected = selectedIds.includes(a.id)
    const bSelected = selectedIds.includes(b.id)

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
        <Table.Root variant="line">
          <TableHeader selectedCount={selectedIds.length} totalCount={knowledgeBases.length} />
          <TableBody
            knowledgeBases={sortedKnowledgeBases}
            selectedIds={selectedIds}
            onRowSelection={handleRowSelection}
          />
        </Table.Root>
      </div>
      {/* <ActionBar hasSelection={selectedIds.length > 0} selectedIds={selectedIds} /> */}
    </>
  )
}

const ActionBar = ({
  hasSelection,
  selectedIds,
}: {
  hasSelection: boolean
  selectedIds: string[]
}) => {
  return (
    <ActionBarChakra.Root open={hasSelection}>
      <Portal>
        <ActionBarChakra.Positioner>
          <ActionBarChakra.Content>
            <ActionBarChakra.SelectionTrigger>
              {selectedIds.length} selected
            </ActionBarChakra.SelectionTrigger>
            <ActionBarChakra.Separator />
            <Button variant="outline" size="sm">
              Process <Kbd>⌘P</Kbd>
            </Button>
            <Button variant="outline" size="sm">
              Export <Kbd>⌘E</Kbd>
            </Button>
          </ActionBarChakra.Content>
        </ActionBarChakra.Positioner>
      </Portal>
    </ActionBarChakra.Root>
  )
}

export default KnowledgeBaseTable
