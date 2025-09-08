import { Checkbox } from "@/components/ui/checkbox"
import { Box, HStack, IconButton, Input, Text, VStack } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import * as React from "react"
import { FiChevronDown, FiChevronUp, FiTrash2 } from "react-icons/fi"

interface SectionItem {
  id: string
  text: string
  consultDocuments: boolean
}

// Individual list item component
interface SectionInteractiveListItemProps {
  index: number
  item: SectionItem
  totalItems: number
  onChange: (id: string, item: SectionItem) => void
  onBlur: (id: string, item: SectionItem) => void
  onRemove: (id: string) => void
  onMoveUp: (id: string) => void
  onMoveDown: (id: string) => void
  canRemove: boolean
  placeholder?: string
}

const SectionInteractiveListItem = ({
  index,
  item,
  totalItems,
  onChange,
  onBlur,
  onRemove,
  onMoveUp,
  onMoveDown,
  canRemove,
  placeholder = "Add section",
}: SectionInteractiveListItemProps) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  const isLastEmptyItem = index === totalItems - 2
  const isAddItem = index === totalItems - 1
  const placeholderText = placeholder

  // Create a stable handler for checkbox changes
  const handleCheckboxChange = (details: any) => {
    onChange(item.id, { ...item, consultDocuments: !!details.checked })
  }

  return (
    <Box
      position="relative"
      display="flex"
      py={2}
      borderRadius="md"
      bg="transparent"
      transition="all 0.2s ease"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      opacity={isAddItem && !isFocused && !isHovered ? 0.6 : 1}
    >
      <HStack align="center" gap={2} w="full">
        {/* Checkbox for document consultation */}
        <Box visibility={isAddItem ? "hidden" : "visible"} minW="120px">
          <Checkbox
            id={`checkbox-${item.id}`}
            checked={item.consultDocuments}
            onCheckedChange={handleCheckboxChange}
            size="sm"
          >
            <Text fontSize="xs">Consult docs</Text>
          </Checkbox>
        </Box>

        <Box flex="1" w="full">
          <Input
            value={item.text}
            onChange={(e) =>
              onChange(item.id, { ...item, text: e.target.value })
            }
            onFocus={() => setIsFocused(true)}
            onBlur={(e) => {
              setIsFocused(false)
              onBlur(item.id, { ...item, text: e.target.value })
            }}
            placeholder={placeholderText}
            size="sm"
            borderTop="none"
            borderLeft="none"
            borderRight="none"
            borderBottom="1px solid"
            borderColor={isFocused ? "blue.300" : "gray.200"}
            borderRadius="none"
            bg="transparent"
            px={2}
            py={0}
            w="full"
            _focus={{
              borderTop: "none",
              borderLeft: "none",
              borderRight: "none",
              borderBottom: "1px solid",
              boxShadow: "none",
              outline: "none",
              bg: "transparent",
            }}
            _placeholder={{
              color: isAddItem ? "gray.400" : "gray.500",
              fontStyle: isAddItem ? "italic" : "normal",
            }}
          />
        </Box>

        <VStack
          visibility={isAddItem ? "hidden" : "visible"}
          gap={0}
          minW="40px"
          align="center"
          py={1}
        >
          <IconButton
            size="xs"
            variant="ghost"
            colorScheme="gray"
            aria-label="Move item up"
            onClick={() => onMoveUp(item.id)}
            opacity={isHovered && index !== 0 ? 1 : 0}
            h="20px"
            w="20px"
            minW="20px"
            pointerEvents={index === 0 ? "none" : "auto"}
          >
            <FiChevronUp size={12} />
          </IconButton>
          <IconButton
            size="xs"
            variant="ghost"
            colorScheme="gray"
            aria-label="Move item down"
            onClick={() => onMoveDown(item.id)}
            pointerEvents={isLastEmptyItem ? "none" : "auto"}
            opacity={isHovered && !isLastEmptyItem ? 1 : 0}
            h="20px"
            w="20px"
            minW="20px"
          >
            <FiChevronDown size={12} />
          </IconButton>
        </VStack>

        <Box opacity={isHovered ? 1 : 0}>
          {canRemove && (
            <IconButton
              size="xs"
              variant="ghost"
              colorPalette="red"
              aria-label="Remove item"
              onClick={(e) => {
                e.stopPropagation()
                onRemove(item.id)
              }}
              h="24px"
              w="24px"
              minW="24px"
            >
              <FiTrash2 size={12} />
            </IconButton>
          )}
        </Box>
      </HStack>
    </Box>
  )
}

// Main Section Interactive List Component that manages the items
interface SectionInteractiveListProps {
  value: string | SectionItem[] // Accept either string with newlines or array of section items
  onChange: (value: string) => void // Always emit string with newlines for consistency
  onStructuredChange?: (items: SectionItem[]) => void // Emit structured data
  placeholder?: string
  minItems?: number
}

export const SectionInteractiveList = ({
  value,
  onChange,
  onStructuredChange,
  placeholder = "Add section",
  minItems = 1,
}: SectionInteractiveListProps) => {
  // Internal state for the list items
  const [items, setItems] = useState<SectionItem[]>([])

  // Use a ref to maintain a counter for stable IDs
  const idCounterRef = React.useRef(0)

  const generateId = () => {
    idCounterRef.current += 1
    return `section-item-${idCounterRef.current}-${Date.now()}`
  }

  // Parse the input value (either string with newlines or array of section items)
  useEffect(() => {
    let newItems: SectionItem[]
    if (typeof value === "string") {
      try {
        // Try to parse as JSON first (structured format)
        const parsedValue = JSON.parse(value)
        if (
          Array.isArray(parsedValue) &&
          parsedValue.every(
            (item) =>
              typeof item === "object" &&
              "text" in item &&
              "consultDocuments" in item,
          )
        ) {
          // It's structured data
          newItems = parsedValue.map((item) => ({
            id: item.id || generateId(),
            text: item.text,
            consultDocuments: item.consultDocuments,
          }))
        } else {
          throw new Error("Not structured format")
        }
      } catch {
        // Fallback to string format (legacy)
        newItems = value
          .split("\n")
          .filter((item) => item.trim() !== "")
          .map((text) => ({
            id: generateId(),
            text: text.trim(),
            consultDocuments: true, // Default to true
          }))
      }
    } else {
      // If it's already an array of section items, use it directly
      newItems = [...value]
    }

    // Always ensure we have at least one empty item at the end
    if (newItems.length === 0 || newItems[newItems.length - 1].text !== "") {
      newItems.push({ id: generateId(), text: "", consultDocuments: true })
    }

    setItems(newItems)
  }, [value])

  // Update items and notify parent components
  const updateItemsAndNotify = (newItems: SectionItem[]) => {
    setItems(newItems)

    // Convert to structured JSON format for backend compatibility
    const structuredData = newItems
      .filter((item) => item.text.trim() !== "")
      .map((item) => ({
        id: item.id,
        text: item.text,
        consultDocuments: item.consultDocuments,
      }))

    const stringValue = JSON.stringify(structuredData)
    onChange(stringValue)

    // Also emit structured data if callback provided
    if (onStructuredChange) {
      const structuredItems = newItems.filter((item) => item.text.trim() !== "")
      onStructuredChange(structuredItems)
    }
  }

  // Update item by ID
  const updateItem = (id: string, newItem: SectionItem) => {
    const newItems = items.map((item) => (item.id === id ? newItem : item))

    // If user is typing in the last empty item, add a new empty item
    const index = items.findIndex((item) => item.id === id)
    if (index === newItems.length - 1 && newItem.text.trim() !== "") {
      newItems.push({ id: generateId(), text: "", consultDocuments: true })
    }

    updateItemsAndNotify(newItems)
  }

  // Handle blur event on item
  const handleItemBlur = (id: string, item: SectionItem) => {
    // Remove empty items (except the last one)
    const index = items.findIndex((i) => i.id === id)
    if (item.text.trim() === "" && index !== items.length - 1) {
      const newItems = items.filter((i) => i.id !== id)
      updateItemsAndNotify(newItems)
    }
  }

  // Remove item by ID
  const removeItem = (id: string) => {
    if (items.length <= minItems) return

    const newItems = items.filter((item) => item.id !== id)
    // Ensure we always have an empty item at the end
    if (newItems.length === 0 || newItems[newItems.length - 1].text !== "") {
      newItems.push({ id: generateId(), text: "", consultDocuments: true })
    }
    updateItemsAndNotify(newItems)
  }

  // Move item up by ID
  const moveItemUp = (id: string) => {
    const index = items.findIndex((item) => item.id === id)
    if (index === 0) return

    const newItems = [...items]
    ;[newItems[index - 1], newItems[index]] = [
      newItems[index],
      newItems[index - 1],
    ]
    updateItemsAndNotify(newItems)
  }

  // Move item down by ID
  const moveItemDown = (id: string) => {
    const index = items.findIndex((item) => item.id === id)
    if (index >= items.length - 2) return // Can't move down past the second to last item

    const newItems = [...items]
    ;[newItems[index], newItems[index + 1]] = [
      newItems[index + 1],
      newItems[index],
    ]
    updateItemsAndNotify(newItems)
  }

  return (
    <VStack align="stretch" gap={0} p={2}>
      {/* Header explaining the checkboxes */}
      <Box mb={2} px={2}>
        <Text fontSize="xs" color="gray.600">
          Check "Consult docs" to generate content from knowledge base, or
          uncheck to use raw text
        </Text>
      </Box>

      {items.map((item, index) => (
        <SectionInteractiveListItem
          key={item.id}
          index={index}
          item={item}
          totalItems={items.length}
          onChange={updateItem}
          onBlur={handleItemBlur}
          onRemove={removeItem}
          onMoveUp={moveItemUp}
          onMoveDown={moveItemDown}
          canRemove={items.length > minItems && index !== items.length - 1}
          placeholder={placeholder}
        />
      ))}
    </VStack>
  )
}
