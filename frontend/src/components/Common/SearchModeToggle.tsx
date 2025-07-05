import { HStack, Text, VStack, Button } from "@chakra-ui/react"

interface SearchModeToggleProps {
  searchMode: "vector" | "full_scan"
  onSearchModeChange: (mode: "vector" | "full_scan") => void
  isDisabled?: boolean
}

const SearchModeToggle = ({
  searchMode,
  onSearchModeChange,
  isDisabled = false,
}: SearchModeToggleProps) => {
  return (
    <VStack align="stretch" gap={2}>
      <Text fontSize="sm" fontWeight="medium">
        Search Method:
      </Text>
      <HStack gap={2}>
        <Button
          size="sm"
          variant={searchMode === "vector" ? "solid" : "outline"}
          onClick={() => onSearchModeChange("vector")}
          disabled={isDisabled}
          colorScheme={searchMode === "vector" ? "blue" : "gray"}
        >
          🔍 Vector Search
        </Button>
        <Button
          size="sm"
          variant={searchMode === "full_scan" ? "solid" : "outline"}
          onClick={() => onSearchModeChange("full_scan")}
          disabled={isDisabled}
          colorScheme={searchMode === "full_scan" ? "blue" : "gray"}
        >
          📄 Full Document Scan
        </Button>
      </HStack>
      <Text fontSize="xs" color="gray.500">
        {searchMode === "vector"
          ? "Finds relevant content using AI similarity search (fast, targeted)"
          : "Analyzes all documents in the knowledge base (comprehensive, thorough)"}
      </Text>
    </VStack>
  )
}

export default SearchModeToggle
