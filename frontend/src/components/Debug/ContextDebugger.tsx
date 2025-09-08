import { Box, Text, VStack } from "@chakra-ui/react"
import type React from "react"
import { useResults } from "../../contexts/ResultsContext"

export const ContextDebugger: React.FC = () => {
  const {
    reviewResults,
    reviewActiveTab,
    generateResult,
    compareResult,
    matchResult,
  } = useResults()

  return (
    <Box
      position="fixed"
      top={4}
      right={4}
      bg="black"
      color="white"
      p={3}
      borderRadius="md"
      fontSize="xs"
      zIndex={9999}
      maxWidth="300px"
    >
      <VStack align="start" gap={1}>
        <Text fontWeight="bold">Context Debug:</Text>
        <Text>
          Review: {reviewResults.length} results, tab {reviewActiveTab}
        </Text>
        <Text>Generate: {generateResult ? "Has result" : "No result"}</Text>
        <Text>Compare: {compareResult ? "Has result" : "No result"}</Text>
        <Text>Match: {matchResult ? "Has result" : "No result"}</Text>
      </VStack>
    </Box>
  )
}
