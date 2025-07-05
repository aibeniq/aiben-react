import { HStack, Text, VStack } from "@chakra-ui/react"
import { Radio, RadioGroup } from "../ui/radio"

interface ReportGenieSearchModeToggleProps {
  searchMode: "vector" | "full_text"
  onSearchModeChange: (mode: "vector" | "full_text") => void
  isDisabled?: boolean
}

const ReportGenieSearchModeToggle = ({
  searchMode,
  onSearchModeChange,
  isDisabled = false,
}: ReportGenieSearchModeToggleProps) => {
  return (
    <VStack align="stretch" gap={2}>
      <Text fontSize="sm" fontWeight="medium">
        Search Mode
      </Text>
      <RadioGroup
        onValueChange={(details) => onSearchModeChange(details.value as "vector" | "full_text")}
        value={searchMode}
        disabled={isDisabled}
      >
        <HStack gap={4}>
          <Radio value="vector">Vector Search</Radio>
          <Radio value="full_text">Full Document Scan</Radio>
        </HStack>
      </RadioGroup>
      <Text fontSize="xs" color="gray.500">
        {searchMode === "vector"
          ? "Finds relevant content using AI similarity search (fast, targeted)"
          : "Analyzes all documents in the knowledge base (comprehensive, thorough)"}
      </Text>
    </VStack>
  )
}

export default ReportGenieSearchModeToggle
