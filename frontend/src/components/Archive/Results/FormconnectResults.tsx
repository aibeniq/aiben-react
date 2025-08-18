import React from "react"
import { Box, Heading, Text, HStack, Badge, VStack } from "@chakra-ui/react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FiFile, FiEdit3 } from "react-icons/fi"

interface FormconnectResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const FormconnectResults: React.FC<FormconnectResultsProps> = ({ selectedReport, components }) => {
  const results = selectedReport.results?.comparison || selectedReport.results?.message || ""

  // Extract metadata for document information
  const metadata = selectedReport.metadata || {}
  const digitizedFiles = metadata.digitized_files || []
  const handwrittenFiles = metadata.handwritten_files || []
  const fieldCount = metadata.field_count || 0
  const searchMode = metadata.search_mode || "unknown"

  return (
    <>
      {/* Document Metadata Information */}
      {(digitizedFiles.length > 0 || handwrittenFiles.length > 0) && (
        <Box mb={6} p={4} borderWidth="1px" borderRadius="md" bg="surface">
          <Heading as="h4" size="sm" mb={3}>
            Document Information
          </Heading>

          <VStack align="stretch" gap={3}>
            <HStack>
              <Text fontSize="sm" fontWeight="medium">
                Search Mode:
              </Text>
              <Badge colorScheme="blue" fontSize="xs">
                {searchMode}
              </Badge>
              <Text fontSize="sm" fontWeight="medium">
                Fields Processed:
              </Text>
              <Badge colorScheme="green" fontSize="xs">
                {fieldCount}
              </Badge>
            </HStack>

            {digitizedFiles.length > 0 && (
              <Box>
                <HStack mb={2}>
                  <FiFile />
                  <Text fontSize="sm" fontWeight="medium">
                    Digitized Documents ({digitizedFiles.length}):
                  </Text>
                </HStack>
                <Box ml={6}>
                  {digitizedFiles.map((filename: string, index: number) => (
                    <Text key={index} fontSize="sm" color="gray.600">
                      • {filename}
                    </Text>
                  ))}
                </Box>
              </Box>
            )}

            {handwrittenFiles.length > 0 && (
              <Box>
                <HStack mb={2}>
                  <FiEdit3 />
                  <Text fontSize="sm" fontWeight="medium">
                    Handwritten Documents ({handwrittenFiles.length}):
                  </Text>
                </HStack>
                <Box ml={6}>
                  {handwrittenFiles.map((filename: string, index: number) => (
                    <Text key={index} fontSize="sm" color="gray.600">
                      • {filename}
                    </Text>
                  ))}
                </Box>
              </Box>
            )}
          </VStack>
        </Box>
      )}

      {/* Main Results */}
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}
    </>
  )
}

export default FormconnectResults
