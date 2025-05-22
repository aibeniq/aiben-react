import { useState, useRef, useEffect } from "react";
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Textarea,
  Spinner,
  Flex,
  useBreakpointValue,
  Icon,
  Field,
  Portal,
  Accordion,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import { FaFileUpload, FaPaperPlane, FaTimes, FaTrash } from "react-icons/fa";
import { FiFileText } from "react-icons/fi";
import { KnowledgeBasesService, ChatService } from "@/client";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{
    content: string;
    metadata: Record<string, any>;
  }>;
}

interface ChatbotPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatbotPanel = ({ isOpen, onClose }: ChatbotPanelProps) => {
  const [selectedKbId, setSelectedKbId] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const panelWidth = useBreakpointValue({ base: "100%", sm: "350px", md: "400px", lg: "450px" });
  const panelHeight = useBreakpointValue({ base: "75vh", md: "70vh" });

  const clearChat = () => {
    setMessages([]);
  };

  // Get knowledge bases
  const { data: knowledgeBases = [] } = useQuery({
    queryKey: ["knowledge-bases"],
    queryFn: async () => {
      const response = await KnowledgeBasesService.readKnowledgeBases({ 
        skip: 0, 
        limit: 100 // Get all knowledge bases
      });
      return response.data || [];
    },
    enabled: isOpen
  });

  // Dropzone for file upload
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setUploadedFile(acceptedFiles[0]);
        setSelectedKbId(null);
      }
    },
    maxFiles: 1,
  });

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!question.trim() || (!selectedKbId && !uploadedFile)) return;

    const userMessage = question;
    
    // Add the new user message to chat history
    const updatedMessages = [...messages, { role: "user", content: userMessage }];
    setMessages(updatedMessages);
    setQuestion("");
    setIsLoading(true);

    try {
      let response;
      
      // Format chat history for API 
      // Only send the last 10 messages to keep context manageable
      const recentHistory = updatedMessages.slice(-10);
      const formattedChatHistory = recentHistory.map(msg => {
        const role = msg.role === "user" ? "User" : "Assistant";
        return `${role}: ${msg.content}`;
      }).join("\n\n");
      
      console.log("Formatted chat history:", formattedChatHistory);

      if (selectedKbId) {
        response = await ChatService.queryKnowledgeBase({
          kbId: selectedKbId,
          question: userMessage,
          chatHistory: formattedChatHistory,  // Send chat history
          useDefaultModels: true
        });
      } else if (uploadedFile) {
        const formData = new FormData();
        formData.append("file", uploadedFile);
        
        response = await ChatService.queryDocument({
          question: userMessage,
          chatHistory: formattedChatHistory,
          useDefaultModels: true,
          formData: {
            file: uploadedFile
          }
        });
      }

      console.log("Response:", response);

      if (response?.answer) {
        // You can show the rephrased question if you want
        const rephrasedInfo = response.rephrased_question && 
          response.rephrased_question !== userMessage ? 
          `(Interpreted as: "${response.rephrased_question}")` : "";
        
        setMessages((prev) => [
          ...prev,
          { 
            role: "assistant", 
            content: response.answer + (rephrasedInfo ? `\n\n${rephrasedInfo}` : ""),
            sources: response.sources,
            rephrasedQuestion: response.rephrased_question
          }
        ]);
      }
    } catch (error) {
      console.error("Error querying:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't process your request. Please try again." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Portal>
      <Box
        position="fixed"
        bottom="70px"
        right="20px"
        width={panelWidth}
        height="auto"
        maxHeight={panelHeight}
        bg="white"
        borderRadius="xl"
        boxShadow="xl"
        overflow="hidden"
        zIndex={1000}
        animation="slideUp 0.2s ease-out"
        display="flex"
        flexDirection="column"
        sx={{
          '@keyframes slideUp': {
            '0%': {
              opacity: 0,
              transform: 'translateY(20px)'
            },
            '100%': {
              opacity: 1,
              transform: 'translateY(0)'
            }
          }
        }}
      >
        {/* Header - Keep fixed */}
        <Box 
          p={3} 
          bg="teal" 
          color="white"
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          flexShrink={0}
        >
          <Text fontWeight="bold">AI Assistant</Text>
          <HStack spacing={2}>
            {messages.length > 0 && (
              <Button
                variant="ghost"
                color="white"
                display="flex"
                alignItems="center"
                justifyContent="center"
                onClick={clearChat}
                size="sm"
                p={1}
                _hover={{ bg: "teal" }}
                title="Clear chat history"
              >
                <Icon as={FaTrash} boxSize="14px" />
              </Button>
            )}
            <Button
              variant="unstyled"
              color="white"
              display="flex"
              alignItems="center"
              justifyContent="center"
              onClick={onClose}
              size="sm"
              p={0}
            >
              <Icon as={FaTimes} />
            </Button>
          </HStack>
        </Box>

        {/* Scrollable content area */}
        <Box
          p={4}
          overflowY="auto"
          flex="1"
          minHeight="200px"
          maxHeight={`calc(${panelHeight} - 48px)`}
        >
          <VStack spacing={4} width="100%" align="stretch">
            {/* Knowledge Base Selection */}
            <Field.Root>
              <Field.Label>Select Knowledge Base</Field.Label>
              <select
                value={selectedKbId || ""}
                onChange={(e) => {
                  setSelectedKbId(e.target.value || null);
                  setUploadedFile(null);
                }}
                disabled={!!uploadedFile}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  borderRadius: '0.375rem',
                  borderColor: '#E2E8F0',
                }}
              >
                <option value="">Choose a knowledge base</option>
                {knowledgeBases.map(kb => (
                  <option key={kb.id} value={kb.id}>
                    {kb.title}
                  </option>
                ))}
              </select>
            </Field.Root>

            <Text fontWeight="medium" alignSelf="flex-start">OR</Text>

            {/* File Upload */}
            <Box position="relative">
              <Box 
                {...getRootProps()}
                p={3} 
                border="2px dashed" 
                borderColor={isDragActive ? "teal" : "gray.300"}
                borderRadius="md" 
                cursor="pointer"
                width="100%"
                bg={uploadedFile ? "green.50" : "transparent"}
                _hover={{ borderColor: "teal" }}
                transition="all 0.2s"
                data-disabled={!!selectedKbId}
              >
                <input {...getInputProps()} />
                <VStack spacing={1}>
                  <Icon as={FaFileUpload} boxSize="20px" color={isDragActive ? "teal" : "gray.500"} />
                  {uploadedFile ? (
                    <Text fontSize="sm">{uploadedFile.name}</Text>
                  ) : (
                    <Text fontSize="sm" textAlign="center">Drop a file here, or click to select</Text>
                  )}
                </VStack>
              </Box>
              
              {/* Remove file button - only shows when a file is uploaded */}
              {uploadedFile && (
                <Button
                  position="absolute"
                  top="-8px"
                  right="-8px"
                  size="xs"
                  colorPalette="red"
                  borderRadius="full"
                  width="24px"
                  height="24px"
                  minWidth="24px"
                  p={0}
                  onClick={(e) => {
                    e.stopPropagation();
                    setUploadedFile(null);
                  }}
                  aria-label="Remove file"
                  title="Remove file"
                >
                  <Icon as={FaTimes} boxSize="10px" />
                </Button>
              )}
            </Box>

            {/* Chat Messages */}
            <Box 
              width="100%" 
              height="300px"
              overflowY="auto" 
              border="1px solid" 
              borderColor="gray.200"
              borderRadius="md"
              p={3}
              bg="gray.50"
            >
              {messages.length === 0 ? (
                <Text color="gray.500" textAlign="center" py={10} fontSize="sm">
                  Select a knowledge base or upload a file, then ask a question.
                </Text>
              ) : (
                <>
                  {messages.map((msg, idx) => (
                    <Box 
                      key={idx} 
                      bg={msg.role === "user" ? "blue.50" : "white"} 
                      p={2} 
                      mb={2}
                      borderRadius="md"
                      alignSelf={msg.role === "user" ? "flex-end" : "flex-start"}
                      maxW="90%"
                      borderWidth="1px"
                      width="100%"
                    >
                      <Text fontSize="sm">{msg.content}</Text>
                      
                      {/* Display sources if available */}
                      {msg.sources && msg.sources.length > 0 && (
                        <Accordion.Root type="single" collapsible mt={2}>
                          <Accordion.Item>
                            <h2>
                              <Accordion.ItemTrigger bg="gray.100" _hover={{ bg: "gray.200" }}>
                                <Box flex="1" textAlign="left" fontWeight="medium">
                                  <HStack>
                                    <Icon as={FiFileText} />
                                    <Text fontSize="xs">
                                      View Source Citations ({msg.sources.length})
                                    </Text>
                                  </HStack>
                                </Box>
                              </Accordion.ItemTrigger>
                            </h2>
                            <Accordion.ItemContent pb={2} bg="gray.50">
                              {msg.sources.map((source, sIdx) => (
                                <Box 
                                  key={sIdx}
                                  p={2} 
                                  mb={2} 
                                  borderWidth="1px" 
                                  borderRadius="md"
                                  bg="white"
                                >
                                  <Text fontWeight="bold" fontSize="xs" color="gray.700">
                                    Source {sIdx + 1}:
                                    {source.metadata?.source && (
                                      <Text as="span" ml={1} fontWeight="normal" color="blue.600">
                                        {/* Clean up temporary file paths */}
                                        {source.metadata.source.includes('/tmp/') || source.metadata.source.includes('\\tmp\\')
                                          ? (() => {
                                              const filename = source.metadata.source.split('/').pop() || 
                                                              source.metadata.source.split('\\').pop() || '';
                                              
                                              return filename.includes('_') 
                                                ? filename.substring(filename.indexOf('_') + 1) 
                                                : filename;
                                            })()
                                          : source.metadata.source}
                                      </Text>
                                    )}
                                  </Text>
                                  <Box 
                                    mt={1} 
                                    p={2} 
                                    bg="gray.50" 
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
                  {isLoading && (
                    <Flex justify="flex-start" mb={3}>
                      <Spinner size="sm" />
                    </Flex>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </Box>
          </VStack>
        </Box>
        
        {/* Input area - Keep fixed at bottom */}
        <HStack width="100%" p={4} pt={2} bg="white" borderTop="1px solid" borderColor="gray.100" flexShrink={0}>
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            resize="none"
            rows={2}
            disabled={(!selectedKbId && !uploadedFile) || isLoading}
            fontSize="sm"
          />
          <Button 
            colorPalette="teal" 
            onClick={handleSendMessage}
            disabled={!question.trim() || (!selectedKbId && !uploadedFile) || isLoading}
            isLoading={isLoading}
            leftIcon={<FaPaperPlane />}
            size="sm"
          >
            Send
          </Button>
        </HStack>
      </Box>
    </Portal>
  );
};

export default ChatbotPanel;