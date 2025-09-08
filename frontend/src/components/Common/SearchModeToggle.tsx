import { HStack, Text, VStack } from "@chakra-ui/react"
import { Radio, RadioGroup } from "../ui/radio"
import HelpTooltip from "../ui/help-tooltip"

interface SearchModeToggleProps {
  searchMode: "vector" | "full_scan"
  onSearchModeChange: (mode: "vector" | "full_scan") => void
  isDisabled?: boolean
  helpKey?: string // Optional help key for tooltip
}

const SearchModeToggle = ({
  searchMode,
  onSearchModeChange,
  isDisabled = false,
  helpKey,
}: SearchModeToggleProps) => {
  return (
    <VStack align="stretch" gap={2}>
      <HStack align="center">
        <Text fontSize="sm" fontWeight="medium">
          Search Mode
        </Text>
        {helpKey && <HelpTooltip helpKey={helpKey} />}
      </HStack>
      <RadioGroup
        onValueChange={(details) => onSearchModeChange(details.value as "vector" | "full_scan")}
        value={searchMode}
        disabled={isDisabled}
      >
        <HStack gap={4}>
          <Radio value="vector">Vector Search</Radio>
          <Radio value="full_scan">Full Document Scan</Radio>
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

export default SearchModeToggle
