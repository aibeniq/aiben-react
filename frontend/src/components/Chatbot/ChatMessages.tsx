import { Box, Text, Flex, Spinner, Accordion, Icon, HStack, Show, VStack } from "@chakra-ui/react"
import { FiFileText } from "react-icons/fi"
import SourceLink from "../Common/SourceLink"
import React from "react"

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
}) => (
  <>
    <Show when={messages.length === 0}>
      <Text color="gray.500" textAlign="center" py={10} fontSize="sm">
        {selectedKbId || uploadedFiles.length > 0
          ? "Select a knowledge base or upload files, then ask a question."
          : "Ask me anything! For knowledge base search, select a knowledge base first."}
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
                    {msg.sources.map((source, sIdx) => (
                      <Box key={sIdx} p={2} mb={2} borderWidth="1px" borderRadius="md" bg="bg">
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
                              />
                            ) : (
                              <Text as="span" ml={1} fontWeight="normal" color="blue.600">
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
                          {source.content}
                        </Box>
                      </Box>
                    ))}
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

export default ChatMessages
