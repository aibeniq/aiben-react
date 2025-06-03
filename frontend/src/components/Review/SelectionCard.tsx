import React from "react"
import { Box, Card, Heading, Text, VStack, HStack } from "@chakra-ui/react"
import { FiCheck, FiX } from "react-icons/fi"

interface SelectionCardProps {
  title: string
  description: string
  icon: React.ReactNode
  isSelected: boolean
  isDisabled?: boolean
  onClick: () => void
}

const SelectionCard = ({
  title,
  description,
  icon,
  isSelected,
  isDisabled = false,
  onClick,
}: SelectionCardProps) => {
  return (
    <Card.Root
      flex="1"
      cursor={isDisabled ? "not-allowed" : "pointer"}
      onClick={isDisabled ? undefined : onClick}
      opacity={isDisabled ? 0.5 : 1}
    >
      <Card.Body p={6}>
        <HStack gap={4} align="center">
          <HStack gap={3} align="center">
            <Box
              p={3}
              borderRadius="full"
              bg={isSelected ? "green.100" : "gray.100"}
              color={isSelected ? "green.600" : "gray.500"}
            >
              {icon}
            </Box>
            <VStack gap={1} align="start">
              <Heading size="md">{title}</Heading>
              <Text fontSize="sm" color="gray.600">
                {description}
              </Text>
            </VStack>
          </HStack>

          <Box color={isSelected ? "green.500" : "gray.400"} ml="auto">
            {isSelected ? <FiCheck size={16} /> : ""}
          </Box>
        </HStack>
      </Card.Body>
    </Card.Root>
  )
}

export default SelectionCard
