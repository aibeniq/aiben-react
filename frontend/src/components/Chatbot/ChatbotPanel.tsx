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
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import { FaFileUpload, FaPaperPlane, FaTimes } from "react-icons/fa";
import { KnowledgeBasesService, ChatService } from "@/client";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
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
    setMessages([...messages, { role: "user", content: userMessage }]);
    setQuestion("");
    setIsLoading(true);

    try {
      let response;
      
      if (selectedKbId) {
        response = await ChatService.askKnowledgeBase({
          knowledgeBaseId: selectedKbId,
          question: userMessage,
          useDefaultModels: true
        });
      } else if (uploadedFile) {
        const formData = new FormData();
        formData.append("file", uploadedFile);
        formData.append("question", userMessage);
        formData.append("useDefaultModels", "true");
        
        response = await ChatService.askDocument({
          requestBody: formData
        });
      }

      if (response?.data) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: response.data.answer }
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
        height={panelHeight}
        bg="white"
        borderRadius="xl"
        boxShadow="xl"
        overflow="hidden"
        zIndex={1000}
        animation="slideUp 0.2s ease-out"
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
        {/* Header */}
        <Box 
          p={3} 
          bg="blue.500" 
          color="white"
          display="flex"
          justifyContent="space-between"
          alignItems="center"
        >
          <Text fontWeight="bold">AI Assistant</Text>
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
        </Box>

        {/* Body */}
        <Box p={4} height="calc(100% - 48px)" display="flex" flexDirection="column">
          <VStack spacing={4} height="100%">
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
            <Box 
              {...getRootProps()}
              p={3} 
              border="2px dashed" 
              borderColor={isDragActive ? "blue.500" : "gray.300"}
              borderRadius="md" 
              cursor="pointer"
              width="100%"
              bg={uploadedFile ? "green.50" : "transparent"}
              _hover={{ borderColor: "blue.500" }}
              transition="all 0.2s"
              data-disabled={!!selectedKbId}
            >
              <input {...getInputProps()} />
              <VStack spacing={1}>
                <Icon as={FaFileUpload} boxSize="20px" color={isDragActive ? "blue.500" : "gray.500"} />
                {uploadedFile ? (
                  <Text fontSize="sm">{uploadedFile.name}</Text>
                ) : (
                  <Text fontSize="sm" textAlign="center">Drop a file here, or click to select</Text>
                )}
              </VStack>
            </Box>

            {/* Chat Messages */}
            <Box 
              flex="1"
              width="100%" 
              overflowY="auto" 
              border="1px solid" 
              borderColor="gray.200"
              borderRadius="md"
              p={3}
              bg="gray.50"
              minHeight="200px"
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
                    >
                      <Text fontSize="sm">{msg.content}</Text>
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

            {/* Input Area */}
            <HStack width="100%">
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
                colorPalette="blue" 
                onClick={handleSendMessage}
                disabled={!question.trim() || (!selectedKbId && !uploadedFile) || isLoading}
                isLoading={isLoading}
                leftIcon={<FaPaperPlane />}
                size="sm"
              >
                Send
              </Button>
            </HStack>
          </VStack>
        </Box>
      </Box>
    </Portal>
  );
};

export default ChatbotPanel;