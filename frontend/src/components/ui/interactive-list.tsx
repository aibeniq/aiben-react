import { Box, HStack, IconButton, Input, VStack } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { FiChevronDown, FiChevronUp, FiTrash2 } from "react-icons/fi"

// Individual list item component
interface InteractiveListItemProps {
  index: number
  value: string
  totalItems: number
  onChange: (index: number, value: string) => void
  onBlur: (index: number, value: string) => void
  onRemove: (index: number) => void
  onMoveUp: (index: number) => void
  onMoveDown: (index: number) => void
  canRemove: boolean
  placeholder?: string
}

const InteractiveListItem = ({
  index,
  value,
  totalItems,
  onChange,
  onBlur,
  onRemove,
  onMoveUp,
  onMoveDown,
  canRemove,
  placeholder = "Add item",
}: InteractiveListItemProps) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  const isLastEmptyItem = index === totalItems - 2
  const isAddItem = index === totalItems - 1
  const placeholderText = placeholder

  return (
    <Box
      position="relative"
      display="flex"
      py={1}
      borderRadius="md"
      bg="transparent"
      transition="all 0.2s ease"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      opacity={isAddItem && !isFocused && !isHovered ? 0.6 : 1}
    >
      <HStack align="center" gap={0} w="full">
        <Box flex="1" w="full">
          <Input
            value={value}
            onChange={(e) => onChange(index, e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={(e) => {
              setIsFocused(false)
              onBlur(index, e.target.value)
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
            onClick={() => onMoveUp(index)}
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
            onClick={() => onMoveDown(index)}
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
                onRemove(index)
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

// Main Interactive List Component that manages the items
interface InteractiveListProps {
  value: string | string[] // Accept either string with newlines or array of strings
  onChange: (value: string) => void // Always emit string with newlines for consistency
  placeholder?: string
  minItems?: number
}

export const InteractiveList = ({
  value,
  onChange,
  placeholder = "Add item",
  minItems = 1,
}: InteractiveListProps) => {
  // Internal state for the list items
  const [items, setItems] = useState<string[]>([])

  // Parse the input value (either string with newlines or array)
  useEffect(() => {
    let newItems: string[]
    if (typeof value === "string") {
      // If it's a string, split by newlines and filter empties
      newItems = value.split("\n").filter((item) => item !== "")
    } else {
      // If it's already an array, use it directly
      newItems = [...value]
    }

    // Always ensure we have at least one empty item at the end
    if (newItems.length === 0 || newItems[newItems.length - 1] !== "") {
      newItems.push("")
    }

    setItems(newItems)
  }, [value])

  // Update item at specific index
  const updateItem = (index: number, newValue: string) => {
    const newItems = [...items]
    newItems[index] = newValue
    updateItemsAndNotify(newItems)
  }

  // Handle blur event on item
  const handleItemBlur = (index: number, value: string) => {
    // Remove empty items (except the last one)
    if (value.trim() === "" && index !== items.length - 1) {
      const newItems = items.filter((_, i) => i !== index)
      updateItemsAndNotify(newItems)
    }
  }

  // Remove item at index
  const removeItem = (index: number) => {
    // Don't allow removing if it would go below minItems
    if (items.filter((item) => item.trim() !== "").length <= minItems) return

    const newItems = items.filter((_, i) => i !== index)
    updateItemsAndNotify(newItems)
  }

  // Move item up
  const moveItemUp = (index: number) => {
    if (index <= 0) return

    const newItems = [...items]
    const temp = newItems[index]
    newItems[index] = newItems[index - 1]
    newItems[index - 1] = temp
    updateItemsAndNotify(newItems)
  }

  // Move item down
  const moveItemDown = (index: number) => {
    if (index >= items.length - 1) return

    const newItems = [...items]
    const temp = newItems[index]
    newItems[index] = newItems[index + 1]
    newItems[index + 1] = temp
    updateItemsAndNotify(newItems)
  }

  // Update internal state and notify parent
  const updateItemsAndNotify = (newItems: string[]) => {
    // Check if we need to add an empty item at the end
    if (newItems.length === 0 || newItems[newItems.length - 1] !== "") {
      newItems.push("")
    }

    setItems(newItems)

    // Notify parent with the new string value (without the last empty item)
    const valueToNotify = newItems
      .slice(0, -1) // Remove the last empty item
      .filter((item) => item.trim() !== "") // Remove any other empty items
      .join("\n")

    onChange(valueToNotify)
  }

  // Automatically add a new empty item at the end when needed
  useEffect(() => {
    const lastItem = items[items.length - 1]
    if (lastItem && lastItem.trim() !== "" && items.length > 0) {
      updateItemsAndNotify([...items, ""])
    }
  }, [items])

  return (
    <VStack align="stretch" width="100%" gap={0}>
      {items.map((item, index) => (
        <InteractiveListItem
          key={index}
          index={index}
          value={item}
          onChange={updateItem}
          onBlur={handleItemBlur}
          onRemove={removeItem}
          onMoveUp={moveItemUp}
          onMoveDown={moveItemDown}
          canRemove={
            items.length > minItems &&
            item.trim() !== "" &&
            index !== items.length - 1
          }
          totalItems={items.length}
          placeholder={placeholder}
        />
      ))}
    </VStack>
  )
}

// Export the individual list item component as well in case it's needed
export { InteractiveListItem }
