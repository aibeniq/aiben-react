import { IconButton, Popover, Icon, Box } from "@chakra-ui/react"
import { FiPlus, FiDatabase, FiFile } from "react-icons/fi"
import React from "react"

interface SourcePopoverProps {
  onSelectKnowledgeBase: () => void
  onSelectFile: () => void
  iconButtonProps?: React.ComponentProps<typeof IconButton>
}

const SourcePopover: React.FC<SourcePopoverProps> = ({
  onSelectKnowledgeBase,
  onSelectFile,
  iconButtonProps,
}) => {
  const handleFileClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onSelectFile()
  }

  return (
    <Popover.Root>
      <Popover.Trigger>
        <IconButton
          aria-label="Add Source"
          variant="ghost"
          borderRadius="none"
          size="md"
          _hover={{
            bg: "transparent",
          }}
          {...iconButtonProps}
        >
          <Icon as={FiPlus} />
        </IconButton>
      </Popover.Trigger>
      <Popover.Positioner>
        <Popover.Content w="200px" color="gray.700" borderRadius="md" boxShadow="lg" border="none">
          <Popover.Arrow>
            <Popover.ArrowTip />
          </Popover.Arrow>
          <Popover.Body p={2}>
            <Box
              as="button"
              display="flex"
              alignItems="center"
              w="100%"
              px={4}
              py={2}
              _hover={{
                borderRadius: "md",
                cursor: "pointer",
                textDecoration: "underline",
              }}
              onClick={onSelectKnowledgeBase}
            >
              <Icon as={FiDatabase} mr={2} />
              Knowledge Base
            </Box>
            <Box
              as="button"
              display="flex"
              alignItems="center"
              w="100%"
              px={4}
              py={2}
              _hover={{
                borderRadius: "md",
                cursor: "pointer",
                textDecoration: "underline",
              }}
              onClick={handleFileClick}
            >
              <Icon as={FiFile} mr={2} />
              File
            </Box>
          </Popover.Body>
        </Popover.Content>
      </Popover.Positioner>
    </Popover.Root>
  )
}

export default SourcePopover
