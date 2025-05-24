import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  Textarea,
  VStack,
  HStack,
  Switch,
  Field as ChakraField,
  Spinner,
  Input,
  Separator,
  Table,
  Accordion,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import SourceLink from "@/components/Common/SourceLink"
import { useState, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import { VeradocService, KnowledgeBasesService } from "@/client"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FiFileText } from "react-icons/fi"
import { Field } from "../../components/ui/field"

const VeraDoc = () => {

  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<any>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<any[]>([]);

  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown";
    
    // Clean up temporary file paths
    if (source.includes('/tmp/') || source.includes('\\tmp\\')) {
      // First get the filename without the path
      const filename = source.split('/').pop() || 
                      source.split('\\').pop() || '';
      
      // Then remove everything before and including the first underscore
      return filename.includes('_') 
        ? filename.substring(filename.indexOf('_') + 1) 
        : filename;
    }
    
    return source;
  };

  // Add this effect to fetch knowledge bases when component mounts
  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        // Assuming your service has a method to fetch knowledge bases
        const response = await KnowledgeBasesService.readKnowledgeBases({ 
          skip: 0, 
          limit: 100 // Get all knowledge bases
        });
        setKnowledgeBases(response.data || []);
      } catch (error) {
        console.error("Error fetching knowledge bases:", error);
      }
    };

    fetchKnowledgeBases();
  }, []);

    // Add these state variables with your other state definitions
    const [selectedKnowledgeBaseDetails, setSelectedKnowledgeBaseDetails] = useState<any>(null);

    // Add this function to fetch knowledge base details including sources
    const fetchKnowledgeBaseDetails = async (knowledgeBaseId: string) => {
      try {
        const response = await KnowledgeBasesService.readKnowledgeBase({ id: knowledgeBaseId });
        setSelectedKnowledgeBaseDetails(response);
      } catch (error) {
        console.error("Error fetching knowledge base details:", error);
        showErrorToast("Failed to fetch knowledge base details");
      }
    };

  const [mode, setMode] = useState<"manual" | "batch">("manual"); // Toggle between Manual and Batch Mode
 
  const [batchFiles, setBatchFiles] = useState<Array<{
    file: File;
    isHandwritten: boolean;
  }>>([]);

  const [batchResults, setBatchResults] = useState<Array<{ displayResults: string; qaPairs: any[] }>>([]);
  const [selectedBatchResult, setSelectedBatchResult] = useState<number>(0);
  const [batchLoading, setBatchLoading] = useState<boolean>(false);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        // Convert the new files to our file item format
        const newFileItems = acceptedFiles.map(file => ({
          file,
          isHandwritten: false
        }));
        
        // Add to existing files
        setBatchFiles(prev => [...prev, ...newFileItems]);
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    multiple: true,
  });

  // Add batch uploader
  const addBatchUploader = () => {
    setBatchFileItems((prev) => [...prev, { files: [], isHandwritten: false }]);
  };

  // Toggle handwritten status for all files in a batch uploader
  const toggleBatchHandwritten = (index: number) => {
    setBatchFileItems((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, isHandwritten: !item.isHandwritten } : item
      )
    );
  };

  const removeBatchUploader = (index: number) => {
    setBatchFileItems((prev) => prev.filter((_, i) => i !== index));
  };

  const addFilesToBatchUploader = (index: number, newFiles: File[]) => {
    setBatchFileItems((prev) =>
      prev.map((item, i) =>
        i === index ? { 
          ...item, 
          files: [...item.files, ...newFiles],
          isHandwritten: item.isHandwritten  // Preserve the handwritten state
        } : item
      )
    );
  };

  const getBatchSetCount = () => {
    // Find the minimum number of files across all batch uploaders
    // This represents how many complete sets we can process
    if (!batchFileItems || batchFileItems.length === 0) return 0;
    
    // Get the number of files in each uploader
    const fileCounts = batchFileItems.map(item => item.files.length);
    
    // Return the minimum (as we can only process as many complete sets as the column with fewest files)
    return Math.min(...fileCounts);
  };
   
  const [fileItems, setFileItems] = useState<Array<{
    file: File;
    isHandwritten: boolean;
  }>>([]);

  const [qaPairs, setQaPairs] = useState<Array<any>>([]);
  const [checklists, setChecklists] = useState([]); // List of checklists
  const [selectedChecklist, setSelectedChecklist] = useState(null); // Currently selected checklist
  const [checklistName, setChecklistName] = useState(""); // Name of the checklist being created/edited
  const [checklistDescription, setChecklistDescription] = useState(""); // Description of the checklist

  const [questions, setQuestions] = useState("")
  const [results, setResults] = useState("")
  const [loading, setLoading] = useState(false);

  const fetchChecklists = async () => {
    try {
      const data = await VeradocService.getChecklists();
      setChecklists(data);
    } catch (error) {
      console.error("Error fetching checklists:", error);
    }
  };

  useEffect(() => {
    fetchChecklists();
  }, []);

  // Add this mutation hook inside your VeraDoc component, before your handleRun function
  const mutation = useMutation({
    mutationFn: (data: {
      questions: string;
      knowledgeBaseId: string;
      files: File[];
      handwrittenFiles: File[];
    }) => {
      console.log("Now beginning RAG mutation...")
      
      // Call the API with the proper structure according to your SDK
      return VeradocService.processRagChecklist({
        questions: data.questions,
        knowledgeBaseId: data.knowledgeBaseId,
        formData: {
          files: data.files,
          handwritten_files: data.handwrittenFiles,
        },
      })
    },
    onSuccess: (data) => {
      console.log("Response data:", data)
      
      setResults(data.results.final_evaluation);

      // Store the QA pairs to render with custom components
      setQaPairs(data.results.qa_pairs || []);
      
    },
    onError: (error) => {
      console.log("RAG mutation unsuccessful!")
      setResults(`Error: ${error.message}`)
    },
  })

  const addFile = (file: File) => {
    setFileItems(prevItems => [...prevItems, { file, isHandwritten: false }])
  }

  const removeFile = (index: number) => {
    setFileItems(prevItems => prevItems.filter((_, i) => i !== index))
  }

  const updateFile = (index: number, file: File) => {
    setFileItems(prevItems => prevItems.map((item, i) => 
      i === index ? { ...item, file } : item
    ))
  }

  const toggleHandwritten = (index: number) => {
    setFileItems(prevItems => prevItems.map((item, i) => 
      i === index ? { ...item, isHandwritten: !item.isHandwritten } : item
    ))
  }

  const handleAddNewFile = () => {
    // This will add a placeholder that will be replaced when the user selects a file
    addFile(new File([], "placeholder"))
  }

  const handleRun = async () => {
    if (fileItems.length < 1) {
      setResults("Please upload at least one file.");
      return;
    }

    if (!questions.trim()) {
      setResults("Please enter at least one question.");
      return;
    }

    if (!selectedKnowledgeBase?.id) {
      setResults("Please select a knowledge base for context.");
      return;
    }

    // Filter out placeholder files and separate into regular vs handwritten
    const validItems = fileItems.filter(item => item.file.size > 0);
    const regularFiles = validItems.filter(item => !item.isHandwritten).map(item => item.file);
    const handwrittenFiles = validItems.filter(item => item.isHandwritten).map(item => item.file);

    if (validItems.length < 1) {
      setResults("Please upload at least one valid file.");
      return;
    }

    const requestData = {
      questions: questions,
      knowledgeBaseId: selectedKnowledgeBase.id,
      files: regularFiles,
      handwrittenFiles: handwrittenFiles,
    };

    console.log("Request Data:", requestData);

    setLoading(true); // Set loading to true
    mutation.mutate(requestData, {
      onSettled: () => {
        setLoading(false); // Set loading to false when the process finishes
      },
    });
  };

  // Update your isBatchConfigValid function
  const isBatchConfigValid = () => {
    if (batchFileItems.length < 2) return false;
    
    // Find the minimum number of files in any column
    const minFileCount = Math.min(...batchFileItems.map(item => item.files.length));
    
    // Valid if we have at least one file in each column
    return minFileCount > 0;
  };

  useEffect(() => {
    // Start with one empty file slot
    if (fileItems.length === 0) {
      handleAddNewFile()
    }
  }, [])

  const handleProcessBatch = async () => {
  if (batchFiles.length === 0) {
    setResults("Error: Please upload at least one file for batch processing.");
    return;
  }
  
  if (!questions.trim()) {
    setResults("Error: Please enter at least one question.");
    return;
  }

  if (!selectedKnowledgeBase?.id) {
    setResults("Error: Please select a knowledge base for context.");
    return;
  }
  
  // Clear previous results
  setBatchResults([]);
  setSelectedBatchResult(0);
  setBatchLoading(true);
  
  try {
    const results: string[] = [];
    
    // Process each file individually
    for (let i = 0; i < batchFiles.length; i++) {
      const fileItem = batchFiles[i];
      
      // Separate files based on handwritten flag
      const regularFiles = fileItem.isHandwritten ? [] : [fileItem.file];
      const handwrittenFiles = fileItem.isHandwritten ? [fileItem.file] : [];
      
      // Process this file
      const requestData = {
        questions: questions,
        knowledgeBaseId: selectedKnowledgeBase.id,
        files: regularFiles,
        handwrittenFiles: handwrittenFiles,
      };
      
      // Call the API using our mutation
      const response = await VeradocService.processRagChecklist({
        questions: requestData.questions,
        knowledgeBaseId: requestData.knowledgeBaseId,
        formData: {
          files: requestData.files,
          handwritten_files: requestData.handwrittenFiles,
        },
      });
      
      // Format the response
      let displayResults = `# Analysis Results for ${fileItem.file.name}\n\n`;

      if (response.results.final_evaluation) {
        displayResults += "## FINAL EVALUATION\n\n";
        displayResults += response.results.final_evaluation + "\n\n";
      }

      // Store the QA pairs in the results array
      results.push({
        displayResults,
        qaPairs: response.results.qa_pairs || []
      });

      // Update your state for batch results
      setBatchResults(results);
    
  }} catch (error) {
    console.error("Batch processing error:", error);
    setResults(`Error processing batch: ${error.message}`);
  } finally {
    setBatchLoading(false);
  }
};

// Create custom components for table rendering
const components = {
  table: (props) => (
    <Box as="table" width="full" borderWidth="1px" borderRadius="md" overflow="hidden" {...props} />
  ),
  thead: (props) => <Box as="thead" bg="gray.100" {...props} />,
  tbody: (props) => <Box as="tbody" {...props} />,
  tr: (props) => <Box as="tr" {...props} />,
  th: (props) => (
    <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
  ),
  td: (props) => (
    <Box as="td" p={4} borderBottomWidth="1px" {...props} />
  ),
};

    return (
    <Container maxW="container.xl" py={8}>
      {/* Add this overlay spinner that shows when batchLoading is true */}
    {batchLoading && (
      <Box
        position="absolute"
        top="0"
        left="0"
        right="0"
        bottom="0"
        bg="rgba(255, 255, 255, 0.7)"
        zIndex="10"
        display="flex"
        alignItems="center"
        justifyContent="center"
        borderRadius="md"
      >
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" thickness="4px" />
          <Text fontWeight="medium">Processing batch files...</Text>
        </VStack>
      </Box>
    )}

      <Heading size="xl" mb={6}>
        VeraDoc
      </Heading>
      
      <VStack spacing={6} align="stretch">
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>Knowledge Base Selection</Heading>
          <Field label="Knowledge Bases" required>
            <select
              value={selectedKnowledgeBase?.id || ""}
              onChange={(e) => {
                const kb = knowledgeBases.find((kb) => kb.id === e.target.value);
                setSelectedKnowledgeBase(kb);
                // When a knowledge base is selected, fetch its sources
                if (kb?.id) {
                  fetchKnowledgeBaseDetails(kb.id);
                }
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                borderRadius: '0.375rem',
                borderColor: '#E2E8F0',
              }}
            >
              <option value="">Select a knowledge base</option>
              {knowledgeBases.map((kb) => (
                <option key={kb.id} value={kb.id}>
                  {kb.title}
                </option>
              ))}
            </select>
          </Field>

          {/* Add this table to display knowledge base sources */}
          {selectedKnowledgeBase && selectedKnowledgeBase.id && (
            <Box mt={4}>
              <Text fontWeight="medium" mb={2}>Sources:</Text>
              {selectedKnowledgeBaseDetails?.files && selectedKnowledgeBaseDetails.files.length > 0 ? (
                <Table.Root variant="simple" size="sm">
                  <Table.Header>
                    <Table.Row>
                      <Table.ColumnHeader>Name</Table.ColumnHeader>
                      <Table.ColumnHeader>Date Added</Table.ColumnHeader>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                    {selectedKnowledgeBaseDetails.files.map((file) => (
                      <Table.Row key={file.id}>
                        <Table.Cell>
                          {/* Make the file name clickable with SourceLink */}
                          <SourceLink
                            sourceId={file.id}
                            fileName={file.name}
                            useModal={true}
                            color="blue.600"
                            _hover={{ textDecoration: "underline" }}
                          />
                        </Table.Cell>
                        <Table.Cell>{new Date(file.date_created || '').toLocaleDateString()}</Table.Cell>
                      </Table.Row>
                    ))}
                  </Table.Body>
                </Table.Root>
              ) : (
                <Text color="gray.500">No sources found for this knowledge base.</Text>
              )}
            </Box>
          )}
        </VStack>        

        {/* Separator before Checklist Selection */}
        <Separator my={4} />

        {/* Checklist Selection and Management */}
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>Checklist Selection</Heading>
          <Field label="Checklists" required>
            <select
              value={selectedChecklist?.id || ""}
              onChange={(e) => {
                const checklist = checklists.find((f) => f.id === e.target.value);
                setSelectedChecklist(checklist);
                setQuestions(checklist?.questions || "");
                setChecklistName(checklist?.name || "");
                setChecklistDescription(checklist?.description || "");
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                borderRadius: '0.375rem',
                borderColor: '#E2E8F0',
              }}
            >
              <option value="">Select a checklist</option>
              {checklists.map((checklist) => (
                <option key={checklist.id} value={checklist.id}>
                  {checklist.name}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Checklist Name" required>
            <Input
              value={checklistName}
              onChange={(e) => setChecklistName(e.target.value)}
              placeholder="Enter checklist name"
            />
          </Field>

          <Field label="Checklist Description">
            <Textarea
              value={checklistDescription}
              onChange={(e) => setChecklistDescription(e.target.value)}
              placeholder="Enter checklist description"
              resize="vertical"
            />
          </Field>

          <Field label="Questions" required>
            <Textarea
              value={questions}
              onChange={(e) => setQuestions(e.target.value)}
              placeholder="Enter questions, one per line"
              rows={6}
              resize="vertical"
            />
          </Field>

          <HStack spacing={4} pt={2}>
            <Button
              variant="solid"
              onClick={async () => {
                try {
                  if (selectedChecklist) {
                    // Update the selected checklist
                    await VeradocService.updateChecklist({
                      checklistId: selectedChecklist.id,
                      requestBody: {
                        name: checklistName,
                        description: checklistDescription,
                        questions,
                      },
                    });

                    alert("Checklist updated successfully.");
                  } else {
                    // Create a new checklist
                    const response = await VeradocService.createChecklist({
                      requestBody: {
                        name: checklistName,
                        description: checklistDescription,
                        questions,
                      },
                    });

                    const newChecklist = await response
                    setChecklists((prev) => [...prev, newChecklist]);
                    alert("Checklist created successfully.");
                  }

                  // Clear the checklist questions and re-fetch the list of checklists
                  setChecklistName("");
                  setChecklistDescription("");
                  setQuestions("");
                  setSelectedChecklist(null);
                  await fetchChecklists();
                } catch (error) {
                  console.error("Error saving checklist:", error);
                  alert("Failed to save checklist. Please try again.");
                }
              }}
            >
              Save Checklist
            </Button>

            <Button
              variant="subtle"
              colorPalette="blue"
              onClick={async () => {
                if (!selectedChecklist) {
                  alert("Please select a checklist to copy.");
                  return;
                }

                try {
                  // Create a copy of the selected checklist
                  const response = await VeradocService.createChecklist({
                    requestBody: {
                      name: `${selectedChecklist.name} (Copy)`,
                      description: selectedChecklist.description,
                      questions: selectedChecklist.questions,
                    },
                  });

                  const newChecklist = await response
                  setChecklists((prev) => [...prev, newChecklist]);
                  alert("Checklist copied successfully.");

                  // Re-fetch the list of checklists
                  await fetchChecklists();
                } catch (error) {
                  console.error("Error copying checklist:", error);
                  alert("Failed to copy checklist. Please try again.");
                }
              }}
              isDisabled={!selectedChecklist}
            >
              Copy Checklist
            </Button>

            <Button
              variant="subtle"
              colorPalette="red"
              onClick={async () => {
                if (!selectedChecklist) {
                  alert("Please select a checklist temmplate to delete.");
                  return;
                }

                try {
                  // Call the deleteChecklist method from VeradocService
                  await VeradocService.deleteChecklist({ checklistId: selectedChecklist.id });

                  // Remove the deleted checklist from the list of checklists
                  setChecklists((prev) => prev.filter((checklist) => checklist.id !== selectedChecklist.id));

                  // Clear the selected checklist and questions
                  setSelectedChecklist(null);
                  setQuestions("");
                  setChecklistName("");
                  setChecklistDescription("");

                  alert("Checklist deleted successfully.");
                } catch (error) {
                  console.error("Error deleting checklist:", error);
                  alert("Failed to delete checklist templtae. Please try again.");
                }
              }}
              isDisabled={!selectedChecklist}
            >
              Delete Checklist
            </Button>
          </HStack>
        </VStack>

      <Separator my={4} />
      <Heading size="md" mb={4}>Document Input</Heading>
      
        
        {/* Mode Toggle */}
        <Field>
          <HStack justify="space-between" align="center">
            <Text fontWeight="medium">Mode:</Text>
            <HStack align="center">
              <Text>Manual</Text>
              <Switch.Root id="mode-toggle" colorPalette="teal">
                <Switch.HiddenInput
                  checked={mode === "batch"}
                  onChange={(e) => setMode(e.target.checked ? "batch" : "manual")}
                />
                <Switch.Control>
                  <Switch.Thumb />
                </Switch.Control>
              </Switch.Root>
              <Text>Batch</Text>
            </HStack>
          </HStack>
        </Field>

        {/* Conditional Rendering Based on Mode */}
        {mode === "manual" ? (
          <VStack spacing={4} align="stretch">
            {/* Manual Mode UI */}
            {fileItems.map((fileItem, index) => (
              <FileDropzone
                key={index}
                index={index}
                fileItem={fileItem}
                onUpdate={updateFile}
                onRemove={removeFile}
                onToggleHandwritten={toggleHandwritten}
              />
            ))}

            <HStack spacing={4}>

              <Button
                variant="solid"
                onClick={handleRun}
                isDisabled={
                  fileItems.length < 1 || !questions.trim() || !fileItems.some((item) => item.file.size > 0)
                }
                loading={loading}
              >
                Run
              </Button>
            </HStack>

            <Separator my={4} />
            <Heading size="md" mb={4}>Results</Heading>

            <Box
              border="1px solid"
              borderColor="gray.200"
              borderRadius="md"
              p={4}
              bg="gray.50"
              minH="100px"
              maxH="400px"
              overflowY="auto"
              position="relative"
              opacity={loading ? 0.5 : 1}
            >
              {loading && (
                <Box
                  position="absolute"
                  top="50%"
                  left="50%"
                  transchecklist="translate(-50%, -50%)"
                  zIndex="1"
                >
                  <Spinner size="lg" color="blue.500" />
                </Box>
              )}
              {results ? (
                <>
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                  {results}
                </ReactMarkdown>

                {qaPairs.length > 0 && (
                  <Box mt={4}>
                    {qaPairs.map((pair, index) => (
                      <Box key={index} mb={4} p={4} borderWidth="1px" borderRadius="md" bg="white">
                        <Heading as="h3" size="md" mb={2}>
                          Question {index + 1}: {pair.question}
                        </Heading>
                        
                        <Box mb={3}>
                          <Text fontWeight="bold">Answer:</Text>
                          <Text>{pair.answer}</Text>
                        </Box>
                        
                        <Box mb={3}>
                          <Text fontWeight="bold">Relevant Policy Context:</Text>
                          <Text>{pair.context}</Text>
                        </Box>
                        
                        {pair.source_citations && pair.source_citations.length > 0 && (
                          <Accordion.Root type="single" collapsible mt={2}>
                            <Accordion.Item>
                              <h2>
                                <Accordion.ItemTrigger bg="gray.100" _hover={{ bg: "gray.200" }}>
                                  <Box flex="1" textAlign="left" fontWeight="medium">
                                    <HStack>
                                      <FiFileText />
                                      <Text>View Source Citations ({pair.source_citations.length})</Text>
                                    </HStack>
                                  </Box>
                                </Accordion.ItemTrigger>
                              </h2>
                              <Accordion.ItemContent pb={4} bg="gray.50">
                                {pair.source_citations.map((citation, cIndex) => (
                                  <Box 
                                    key={cIndex}
                                    p={3} 
                                    mb={2} 
                                    borderWidth="1px" 
                                    borderRadius="md"
                                    bg="white"
                                  >
                                    {citation.metadata.source_data_id ? (
                                        <SourceLink
                                          sourceId={citation.metadata.source_data_id}
                                          fileName={getDisplayFileName(citation.metadata.source)}
                                          ml={1}
                                          fontWeight="normal"
                                          color="blue.600"
                                          useModal={true}
                                        />
                                      ) : (
                                        <Text as="span" ml={1} fontWeight="normal" color="blue.600">
                                          {getDisplayFileName(citation.metadata.source)}
                                        </Text>
                                      )}
                                    <Box 
                                      mt={2} 
                                      p={2} 
                                      bg="gray.50" 
                                      borderRadius="sm" 
                                      fontSize="sm"
                                      whiteSpace="pre-wrap"
                                    >
                                      {citation.content}
                                    </Box>
                                  </Box>
                                ))}
                              </Accordion.ItemContent>
                            </Accordion.Item>
                          </Accordion.Root>
                        )}
                      </Box>
                    ))}
                  </Box>
                  )}
                </>
              ) : (
                <Text color="gray.500">Results will appear here after running.</Text>
              )}
            </Box>
          </VStack>
        ) : (
          <VStack spacing={4} align="stretch">
            {/* File Upload Area */}
            <Box
              border="2px dashed"
              borderColor="gray.300"
              borderRadius="md"
              p={6}
              textAlign="center"
              cursor="pointer"
              _hover={{ borderColor: "blue.500", bg: "blue.50" }}
              {...getRootProps()} // Use useDropzone directly in the component
            >
              <input {...getInputProps()} />
              <VStack spacing={2}>
                <Text>Drag and drop files here, or click to browse</Text>
                <Text fontSize="sm" color="gray.500">
                  You can upload multiple files at once
                </Text>
              </VStack>
            </Box>

            {/* Uploaded Files List */}
            {batchFiles.length > 0 && (
              <Box>
                <Text fontWeight="medium" mb={2}>
                  Uploaded Files ({batchFiles.length})
                </Text>
                <VStack align="stretch" spacing={2} maxH="300px" overflowY="auto">
                  {batchFiles.map((fileItem, index) => (
                    <HStack
                      key={fileItem.file.name + index} // More reliable key
                      justify="space-between"
                      bg="white"
                      p={3}
                      borderRadius="md"
                      border="1px solid"
                      borderColor="gray.200"
                    >
                      <Box>
                        <Text fontWeight="medium" noOfLines={1}>
                          {fileItem.file.name}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {(fileItem.file.size / 1024).toFixed(1)} KB
                        </Text>
                      </Box>
                      <HStack>
                        <ChakraField.Root display="flex" alignItems="center" width="auto">
                          <ChakraField.Label htmlFor={`batch-handwritten-${index}`} mb="0" fontSize="sm">
                            Handwritten
                          </ChakraField.Label>
                          <Switch.Root id={`batch-handwritten-${index}`} colorPalette="blue">
                            <Switch.HiddenInput 
                              checked={fileItem.isHandwritten} 
                              onChange={() => {
                                setBatchFiles(prev => 
                                  prev.map((item, i) => 
                                    i === index ? { ...item, isHandwritten: !item.isHandwritten } : item
                                  )
                                );
                              }}
                            />
                            <Switch.Control>
                              <Switch.Thumb />
                            </Switch.Control>
                          </Switch.Root>
                        </ChakraField.Root>
                        <Button 
                          size="sm" 
                          colorPalette="red" 
                          onClick={() => {
                            setBatchFiles(prev => prev.filter((_, i) => i !== index));
                          }}
                        >
                          Remove
                        </Button>
                      </HStack>
                    </HStack>
                  ))}
                </VStack>
              </Box>
            )}

            {/* Process Button */}
            <HStack spacing={4}>
              <Button 
                variant="solid"
                colorPalette={batchFiles.length > 0 ? "blue" : "gray"}
                onClick={handleProcessBatch}
                isLoading={batchLoading}
                isDisabled={batchFiles.length === 0}
              >
                {batchFiles.length > 0 
                  ? `Process ${batchFiles.length} Files` 
                  : "No Files to Process"}
              </Button>
            </HStack>

            {/* Results section */}
            <Separator my={4} />
            <Heading size="md" mb={4}>Results</Heading>
            <Box>
              {batchResults.length > 0 ? (
                <Field label="Select File to View Results">
                  <select
                    value={selectedBatchResult}
                    onChange={(e) => setSelectedBatchResult(Number(e.target.value))}
                    style={{ 
                      width: '100%',
                      padding: '0.5rem', 
                      borderRadius: '0.375rem',
                      borderColor: '#E2E8F0'
                    }}
                  >
                    {batchResults.map((_, index) => (
                      <option key={index} value={index}>
                        {/* Display file name when available */}
                        {batchFiles[index]?.file?.name || `File ${index + 1}`}
                      </option>
                    ))}
                  </select>
                </Field>
              ) : null}
              
              <Box
                border="1px solid"
                borderColor="gray.200"
                borderRadius="md"
                p={4}
                bg="gray.50"
                minH="100px"
                maxH="400px"
                overflowY="auto"
                position="relative"
                opacity={batchLoading ? 0.5 : 1}
              >
                {batchLoading ? (
                  <Box
                    position="absolute"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    zIndex="1"
                  >
                    <Spinner size="lg" color="blue.500" />
                  </Box>
                ) : (
                  batchResults.length > 0 ? (
                    <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {batchResults[selectedBatchResult].displayResults}
                    </ReactMarkdown>

                    <Box mt={4}>
                      {batchResults[selectedBatchResult].qaPairs.map((pair, index) => (
                        <Box key={index} mb={4} p={4} borderWidth="1px" borderRadius="md" bg="white">
                          <Heading as="h3" size="md" mb={2}>
                            Question {index + 1}: {pair.question}
                          </Heading>
                          
                          <Box mb={3}>
                            <Text fontWeight="bold">Answer:</Text>
                            <Text>{pair.answer}</Text>
                          </Box>
                          
                          <Box mb={3}>
                            <Text fontWeight="bold">Relevant Policy Context:</Text>
                            <Text>{pair.context}</Text>
                          </Box>
                          
                          {pair.source_citations && 
                            console.log("Source citations:", pair.source_citations)}
                          {pair.source_citations && pair.source_citations.length > 0 && (
                            <Accordion.Root type="single" collapsible mt={2}>
                              <Accordion.Item>
                                <h2>
                                  <Accordion.ItemTrigger bg="gray.100" _hover={{ bg: "gray.200" }}>
                                    <Box flex="1" textAlign="left" fontWeight="medium">
                                      <HStack>
                                        <FiFileText />
                                        <Text>View Source Citations ({pair.source_citations.length})</Text>
                                      </HStack>
                                    </Box>
                                  </Accordion.ItemTrigger>
                                </h2>
                                <Accordion.ItemContent pb={4} bg="gray.50">
                                  {pair.source_citations.map((citation, cIndex) => (
                                    <Box 
                                      key={cIndex}
                                      p={3} 
                                      mb={2} 
                                      borderWidth="1px" 
                                      borderRadius="md"
                                      bg="white"
                                    >
                                      {citation.metadata.source_data_id ? (
                                        <SourceLink
                                          sourceId={citation.metadata.source_data_id}
                                          fileName={getDisplayFileName(citation.metadata.source)}
                                          ml={1}
                                          fontWeight="normal" 
                                          color="blue.600"
                                          useModal={true}
                                        />
                                      ) : (
                                        <Text as="span" ml={1} fontWeight="normal" color="blue.600">
                                          {getDisplayFileName(citation.metadata.source)}
                                        </Text>
                                      )}
                                      <Box 
                                        mt={2} 
                                        p={2} 
                                        bg="gray.50" 
                                        borderRadius="sm" 
                                        fontSize="sm"
                                        whiteSpace="pre-wrap"
                                      >
                                        {citation.content}
                                      </Box>
                                    </Box>
                                  ))}
                                </Accordion.ItemContent>
                              </Accordion.Item>
                            </Accordion.Root>
                          )}
                        </Box>
                      ))}
                    </Box>
                    </>
                  ) : (
                    <Text color="gray.500">Results will appear here after processing files.</Text>
                  )
                )}
              </Box>
            </Box>
          </VStack>
        )}
      </VStack>
    </Container>
  )
}

const FileDropzone = ({ 
  index, 
  fileItem, 
  onUpdate, 
  onRemove, 
  onToggleHandwritten 
}: { 
  index: number, 
  fileItem: { file: File, isHandwritten: boolean }, 
  onUpdate: (index: number, file: File) => void,
  onRemove: (index: number) => void,
  onToggleHandwritten: (index: number) => void
}) => {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpdate(index, acceptedFiles[0])
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlchecklistats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/gif": [".gif"],
      "image/bmp": [".bmp"],
      "image/tiff": [".tif", ".tiff"],
      "image/webp": [".webp"],
    },
    multiple: false,
  })

  const { file, isHandwritten } = fileItem
  
  // Check if file is a placeholder
  const isPlaceholder = file && file.name === "placeholder" && file.size === 0

  return (
    <Box position="relative">
      <VStack align="stretch" spacing={2}>
        <Box
          {...getRootProps()}
          border="2px dashed"
          borderColor="gray.300"
          borderRadius="md"
          p={4}
          textAlign="center"
          cursor="pointer"
          _hover={{ borderColor: "blue.500" }}
        >
          <input {...getInputProps()} />
          <Text>
            {file && !isPlaceholder 
              ? `Selected File: ${file.name}` 
              : `Drag and drop File ${index + 1} here, or click to browse`
            }
          </Text>
        </Box>
        
        {/* Only show toggle if a real file is uploaded */}
        {file && !isPlaceholder && (
          <HStack justify="space-between" px={2}>
            <ChakraField.Root display="flex" alignItems="center" width="auto">
              <ChakraField.Label htmlFor={`handwritten-${index}`} mb="0" fontSize="sm">
                Analyze handwriting
              </ChakraField.Label>
              <Switch.Root id={`handwritten-${index}`} colorPalette="blue">
                <Switch.HiddenInput 
                  checked={isHandwritten} 
                  onChange={() => onToggleHandwritten(index)} 
                />
                <Switch.Control>
                  <Switch.Thumb />
                </Switch.Control>
              </Switch.Root>
            </ChakraField.Root>
            
            <Button 
              size="sm" 
              colorScheme="red" 
              onClick={(e) => {
                e.stopPropagation()
                onRemove(index)
              }}
            >
              Remove
            </Button>
          </HStack>
        )}
      </VStack>
    </Box>
  )
}

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/veradoc")({
  component: VeraDoc,
})