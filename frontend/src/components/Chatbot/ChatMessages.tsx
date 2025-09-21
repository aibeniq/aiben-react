import {
  Accordion,
  Box,
  Button,
  Flex,
  HStack,
  Icon,
  Show,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import type React from "react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { FiFileText } from "react-icons/fi"
import SourceLink from "../Common/SourceLink"
import { cleanRTFFormatting } from "../../utils/rtfCleaner"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
  sources?: Array<{
    content: string
    metadata: Record<string, any>
  }>
  rephrasedQuestion?: string
  sessionId?: string
}

interface ChatMessagesProps {
  messages: ChatMessage[]
  isLoading: boolean
  selectedKbId: string | null
  uploadedFiles: File[]
  messagesEndRef: React.RefObject<HTMLDivElement>
}

function getDisplayFileName(source: string): string {
  if (!source) return "Unknown"
  if (source.includes("/tmp/") || source.includes("\\tmp\\")) {
    const filename = source.split("/").pop() || source.split("\\").pop() || ""
    return filename.includes("_") ? filename.substring(filename.indexOf("_") + 1) : filename
  }
  return source
}

const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isLoading,
  selectedKbId,
  uploadedFiles,
  messagesEndRef,
}) => {
  const { t } = useTranslation()

  // State to track which citations are expanded - using object instead of Set
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({})

  // Function to toggle citation expansion
  const toggleCitationExpansion = (messageIndex: number, sourceIndex: number) => {
    const citationKey = `${messageIndex}-${sourceIndex}`
    setExpandedCitations((prev) => ({
      ...prev,
      [citationKey]: !prev[citationKey],
    }))
  }

  // Function to check if a citation is expanded
  const isCitationExpanded = (messageIndex: number, sourceIndex: number) => {
    const citationKey = `${messageIndex}-${sourceIndex}`
    return expandedCitations[citationKey] || false
  }

  return (
    <>
      <Show when={messages.length === 0}>
        <Text color="gray.500" textAlign="center" py={10} fontSize="sm">
          {selectedKbId || uploadedFiles.length > 0
            ? t("chatbot.welcomeMessageWithSource")
            : t("chatbot.welcomeMessageGeneral")}
        </Text>
      </Show>
      <Show when={messages.length > 0}>
        <VStack gap={2} overflowY="auto">
          {messages.map((msg, idx) => (
            <Box
              key={idx}
              bg={msg.role === "user" ? "gray.subtle" : "transparent"}
              px={4}
              py={2}
              borderRadius="md"
              justifyContent={msg.role === "user" ? "flex-end" : "flex-start"}
              maxW="90%"
              width="fit-content"
              alignSelf={msg.role === "user" ? "flex-end" : "flex-start"}
            >
              <Text fontSize="sm">{msg.content}</Text>
              {msg.sources && msg.sources.length > 0 && (
                <Accordion.Root collapsible mt={2}>
                  <Accordion.Item value="sources">
                    <h2>
                      <Accordion.ItemTrigger
                        bg="gray.100 _dark:gray.700"
                        _hover={{ bg: "gray.200 _dark:gray.600" }}
                      >
                        <Box flex="1" textAlign="left" fontWeight="medium">
                          <HStack>
                            <Icon as={FiFileText} />
                            <Text fontSize="xs">View Source Citations ({msg.sources.length})</Text>
                          </HStack>
                        </Box>
                      </Accordion.ItemTrigger>
                    </h2>
                    <Accordion.ItemContent pb={2} bg="gray.50 _dark:gray.900">
                      {msg.sources.map((source, sIdx) => {
                        const isExpanded = isCitationExpanded(idx, sIdx)
                        const citationText = cleanRTFFormatting(source.content)
                        const shouldTruncate = citationText.length > 300
                        const displayText =
                          shouldTruncate && !isExpanded
                            ? `${citationText.substring(0, 300)}...`
                            : citationText

                        return (
                          <Box
                            key={`${idx}-${sIdx}`}
                            p={2}
                            mb={2}
                            borderWidth="1px"
                            borderRadius="md"
                            bg="bg"
                          >
                            <Text fontWeight="bold" fontSize="xs" color="gray.700">
                              Source {sIdx + 1}:
                              {source.metadata?.source &&
                                (source.metadata.source_data_id ? (
                                  <SourceLink
                                    sourceId={source.metadata.source_data_id}
                                    fileName={getDisplayFileName(source.metadata.source)}
                                    ml={1}
                                    fontWeight="normal"
                                    color="blue.600"
                                    useModal={true}
                                    highlightSnippet={citationText}
                                  />
                                ) : (
                                  // For temporary uploaded files without source_data_id, show as plain text
                                  <Text as="span" ml={1} fontWeight="normal" color="gray.600">
                                    {getDisplayFileName(source.metadata.source)}
                                  </Text>
                                ))}
                            </Text>
                            <Box
                              mt={1}
                              p={2}
                              bg="gray.50 _dark:gray.900"
                              borderRadius="sm"
                              fontSize="xs"
                              whiteSpace="pre-wrap"
                            >
                              {displayText}
                            </Box>
                            {shouldTruncate && (
                              <Button
                                size="xs"
                                variant="ghost"
                                mt={1}
                                onClick={(e) => {
                                  e.stopPropagation()
                                  toggleCitationExpansion(idx, sIdx)
                                }}
                                colorPalette="blue"
                              >
                                {isExpanded ? "Show Less" : "Read More"}
                              </Button>
                            )}
                          </Box>
                        )
                      })}
                    </Accordion.ItemContent>
                  </Accordion.Item>
                </Accordion.Root>
              )}
            </Box>
          ))}
          <Show when={isLoading}>
            <Flex justify="flex-start" mb={3}>
              <Spinner size="sm" />
            </Flex>
          </Show>
          <div ref={messagesEndRef} />
        </VStack>
      </Show>
    </>
  )
}

export default ChatMessages
