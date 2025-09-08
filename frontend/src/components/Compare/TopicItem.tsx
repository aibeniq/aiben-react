import { HStack, IconButton, Input, VStack } from "@chakra-ui/react"
import { useState } from "react"
import { FiChevronDown, FiChevronUp, FiTrash2 } from "react-icons/fi"

interface TopicItemProps {
  index: number
  topic: string
  onUpdate: (index: number, value: string) => void
  onBlur: (index: number, value: string) => void
  onRemove: (index: number) => void
  onMoveUp: (index: number) => void
  onMoveDown: (index: number) => void
  canRemove: boolean
  totalTopics: number
}

const TopicItem = ({
  index,
  topic,
  onUpdate,
  onBlur,
  onRemove,
  onMoveUp,
  onMoveDown,
  canRemove,
  totalTopics,
}: TopicItemProps) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  const isLastEmptyTopic = index === totalTopics - 2
  const isAddTopic = index === totalTopics - 1
  const placeholderText = "Add comparison topic"

  return (
    <div
      style={{
        position: "relative",
        display: "flex",
        paddingTop: "0.25rem",
        paddingBottom: "0.25rem",
        borderRadius: "0.375rem",
        backgroundColor: "transparent",
        transition: "all 0.2s ease",
        opacity: isAddTopic && !isFocused && !isHovered ? 0.6 : 1,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <HStack align="center" gap={0} w="full">
        <div style={{ flex: "1", width: "100%" }}>
          <Input
            value={topic}
            onChange={(e) => onUpdate(index, e.target.value)}
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
              color: isAddTopic ? "gray.400" : "gray.500",
              fontStyle: isAddTopic ? "italic" : "normal",
            }}
          />
        </div>

        <VStack
          visibility={isAddTopic ? "hidden" : "visible"}
          gap={0}
          minW="40px"
          align="center"
          py={1}
        >
          <IconButton
            size="xs"
            variant="ghost"
            colorScheme="gray"
            aria-label="Move topic up"
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
            aria-label="Move topic down"
            onClick={() => onMoveDown(index)}
            pointerEvents={isLastEmptyTopic ? "none" : "auto"}
            opacity={isHovered && !isLastEmptyTopic ? 1 : 0}
            h="20px"
            w="20px"
            minW="20px"
          >
            <FiChevronDown size={12} />
          </IconButton>
        </VStack>

        <div style={{ opacity: isHovered ? 1 : 0 }}>
          {canRemove && (
            <IconButton
              size="xs"
              variant="ghost"
              colorPalette="red"
              aria-label="Remove topic"
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
        </div>
      </HStack>
    </div>
  )
}

export default TopicItem
