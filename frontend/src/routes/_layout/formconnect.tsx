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
} from "@chakra-ui/react"
import { useState, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import { FormconnectService } from "@/client"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd' 
import { FaPlus, FaArrowsAlt } from "react-icons/fa"
import { Field } from "../../components/ui/field"

const FormConnect = () => {
  const [mode, setMode] = useState<"manual" | "batch">("manual"); // Toggle between Manual and Batch Mode
  // Update the state definition to include isHandwritten at the item level
const [batchFileItems, setBatchFileItems] = useState<Array<{ 
  files: Array<File>;
    isHandwritten: boolean;
  }>>([
    { files: [], isHandwritten: false },
  ]);

  const [batchResults, setBatchResults] = useState<string[]>([]);
  const [selectedBatchResult, setSelectedBatchResult] = useState<number>(0);
  const [batchLoading, setBatchLoading] = useState<boolean>(false);

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
  

  const moveFileInColumn = (colIndex: number, fileIndex: number, direction: 'up' | 'down') => {
  setBatchFileItems((prev) => {
    const newItems = [...prev];
    const files = [...newItems[colIndex].files];
    
    // Calculate the new position
    const newIndex = direction === 'up' ? fileIndex - 1 : fileIndex + 1;
    
    // Check if the new index is valid
    if (newIndex < 0 || newIndex >= files.length) return prev;
    
    // Swap the files
    const temp = files[fileIndex];
    files[fileIndex] = files[newIndex];
    files[newIndex] = temp;
    
    // Update the files in the column
    newItems[colIndex] = {
      ...newItems[colIndex],
      files: files
    };
    
    return newItems;
  });
};

  const reorderFilesInBatchUploader = (index: number, newFiles: File[]) => {
    setBatchFileItems((prev) =>
      prev.map((item, i) => (i === index ? { files: newFiles } : item))
    );
  };

  const removeFileFromBatchUploader = (uploaderIndex: number, fileIndex: number) => {
    setBatchFileItems((prev) =>
      prev.map((item, i) =>
        i === uploaderIndex
          ? { files: item.files.filter((_, j) => j !== fileIndex) }
          : item
      )
    );
  };
  
  const [fileItems, setFileItems] = useState<Array<{
    file: File;
    isHandwritten: boolean;
  }>>([]);

  const [forms, setForms] = useState([]); // List of forms
  const [selectedForm, setSelectedForm] = useState(null); // Currently selected form
  const [formName, setFormName] = useState(""); // Name of the form being created/edited
  const [formDescription, setFormDescription] = useState(""); // Description of the form

  const [fields, setFields] = useState("")
  const [results, setResults] = useState("")
  const [loading, setLoading] = useState(false);

  const fetchForms = async () => {
    try {
      const data = await FormconnectService.getForms();
      setForms(data);
    } catch (error) {
      console.error("Error fetching forms:", error);
    }
  };

  useEffect(() => {
    fetchForms();
  }, []);

  const mutation = useMutation({
    mutationFn: (data: {
      fields: string;
      digitized_files: File[];
      handwritten_files: File[];
    }) => {
      console.log("Now beginning mutation...")
      
      return FormconnectService.processForm({
        fields: data.fields,
        formData: {
          digitized_files: data.digitized_files,
          handwritten_files: data.handwritten_files,
        },
      })
    },
    onSuccess: (data) => {
      console.log("Response data:", data)
      // Handle both comparison and single file responses
      if (data.results.comparison) {
        console.log("Comparison data:", data.results.comparison)
        setResults(data.results.comparison)
      } else if (data.results.message) {
        setResults(`${data.results.message}\n\n${JSON.stringify(data.results.extracted_data, null, 2)}`)
      } else {
        setResults(JSON.stringify(data.results, null, 2))
      }
    },
    onError: (error) => {
      console.log("Mutation unsuccessful!")
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

    if (!fields.trim()) {
      setResults("Please enter at least one field.");
      return;
    }

    // Filter out placeholder files and separate into digitized vs handwritten
    const validItems = fileItems.filter(item => item.file.size > 0);
    const digitizedFiles = validItems.filter(item => !item.isHandwritten).map(item => item.file);
    const handwrittenFiles = validItems.filter(item => item.isHandwritten).map(item => item.file);

    const requestData = {
      fields: fields,
      digitized_files: digitizedFiles,
      handwritten_files: handwrittenFiles,
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
    // Validate: At least 2 batch uploaders
    if (batchFileItems.length < 2) {
      setResults("Error: Batch processing requires at least 2 batch uploaders.");
      return;
    }
    
    // Check if all batch uploaders have the same number of files
    const fileCount = batchFileItems[0].files.length;
    if (fileCount === 0) {
      setResults("Error: Each batch uploader must contain at least 1 file.");
      return;
    }
    
    const allSameCount = batchFileItems.every(item => item.files.length === fileCount);
    if (!allSameCount) {
      setResults("Error: All batch uploaders must contain the same number of files.");
      return;
    }
    
    // Clear previous results
    setBatchResults([]);
    setSelectedBatchResult(0);
    setBatchLoading(true);
    
    try {
      // Process each "row" of files (1st from each uploader, then 2nd, etc.)
      const results: string[] = [];
      
      for (let fileIndex = 0; fileIndex < fileCount; fileIndex++) {
        // Collect files from each uploader at the current index
        const rowFiles = batchFileItems.map(item => ({
          file: item.files[fileIndex],
          isHandwritten: item.isHandwritten
        }));
        
        // Separate into digitized and handwritten files
        const digitizedFiles = rowFiles.filter(item => !item.isHandwritten).map(item => item.file);
        const handwrittenFiles = rowFiles.filter(item => item.isHandwritten).map(item => item.file);
        
        // Skip processing if there are no fields defined
        if (!fields.trim()) {
          results.push("Error: No fields defined.");
          continue;
        }
        
        // Process this batch row
        const requestData = {
          fields: fields,
          formData: {
            digitized_files: digitizedFiles,
            handwritten_files: handwrittenFiles,
          },
        };
        
        // Call the API
        const response = await FormconnectService.processForm(requestData);
        
        // Format the result based on the response structure
        let resultText = "";
        if (response.results.comparison) {
          resultText = response.results.comparison;
        } else if (response.results.message) {
          resultText = `${response.results.message}\n\n${JSON.stringify(response.results.extracted_data, null, 2)}`;
        } else {
          resultText = JSON.stringify(response.results, null, 2);
        }
        
        results.push(resultText);
      }
      
      // Update state with all results
      setBatchResults(results);
      
    } catch (error) {
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
        FormConnect
      </Heading>
      
      <VStack spacing={6} align="stretch">
        {/* Form Selection and Management */}
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>Form Template Selection</Heading>
          <Field label="Form Templates" required>
            <select
              value={selectedForm?.id || ""}
              onChange={(e) => {
                const form = forms.find((f) => f.id === e.target.value);
                setSelectedForm(form);
                setFields(form?.fields || "");
                setFormName(form?.name || "");
                setFormDescription(form?.description || "");
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                borderRadius: '0.375rem',
                borderColor: '#E2E8F0',
              }}
            >
              <option value="">Select a form</option>
              {forms.map((form) => (
                <option key={form.id} value={form.id}>
                  {form.name}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Form Template Name" required>
            <Input
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="Enter form name"
            />
          </Field>

          <Field label="Form Template Description">
            <Textarea
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              placeholder="Enter form template description"
              resize="vertical"
            />
          </Field>

          <Field label="Fields" required>
            <Textarea
              value={fields}
              onChange={(e) => setFields(e.target.value)}
              placeholder="Enter fields, one per line"
              rows={6}
              resize="vertical"
            />
          </Field>

          <HStack spacing={4} pt={2}>
            <Button
              variant="solid"
              onClick={async () => {
                try {
                  if (selectedForm) {
                    // Update the selected form
                    await FormconnectService.updateForm({
                      formId: selectedForm.id,
                      requestBody: {
                        name: formName,
                        description: formDescription,
                        fields,
                      },
                    });

                    alert("Form template updated successfully.");
                  } else {
                    // Create a new form
                    const response = await FormconnectService.createForm({
                      requestBody: {
                        name: formName,
                        description: formDescription,
                        fields,
                      },
                    });

                    const newForm = await response
                    setForms((prev) => [...prev, newForm]);
                    alert("Form template created successfully.");
                  }

                  // Clear the form fields and re-fetch the list of forms
                  setFormName("");
                  setFormDescription("");
                  setFields("");
                  setSelectedForm(null);
                  await fetchForms();
                } catch (error) {
                  console.error("Error saving form template:", error);
                  alert("Failed to save form template. Please try again.");
                }
              }}
            >
              Save Form Template
            </Button>

            <Button
              variant="subtle"
              colorPalette="blue"
              onClick={async () => {
                if (!selectedForm) {
                  alert("Please select a form template to copy.");
                  return;
                }

                try {
                  // Create a copy of the selected form
                  const response = await FormconnectService.createForm({
                    requestBody: {
                      name: `${selectedForm.name} (Copy)`,
                      description: selectedForm.description,
                      fields: selectedForm.fields,
                    },
                  });

                  const newForm = await response
                  setForms((prev) => [...prev, newForm]);
                  alert("Form template copied successfully.");

                  // Re-fetch the list of forms
                  await fetchForms();
                } catch (error) {
                  console.error("Error copying form template:", error);
                  alert("Failed to copy form template. Please try again.");
                }
              }}
              isDisabled={!selectedForm}
            >
              Copy Form Template
            </Button>

            <Button
              variant="subtle"
              colorPalette="red"
              onClick={async () => {
                if (!selectedForm) {
                  alert("Please select a form temmplate to delete.");
                  return;
                }

                try {
                  // Call the deleteForm method from FormconnectService
                  await FormconnectService.deleteForm({ formId: selectedForm.id });

                  // Remove the deleted form from the list of forms
                  setForms((prev) => prev.filter((form) => form.id !== selectedForm.id));

                  // Clear the selected form and fields
                  setSelectedForm(null);
                  setFields("");
                  setFormName("");
                  setFormDescription("");

                  alert("Form template deleted successfully.");
                } catch (error) {
                  console.error("Error deleting form template:", error);
                  alert("Failed to delete form templtae. Please try again.");
                }
              }}
              isDisabled={!selectedForm}
            >
              Delete Form Template
            </Button>
          </HStack>
        </VStack>

      <Separator my={4} />
      <Heading size="md" mb={4}>File Input</Heading>
      
        
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
              <Button variant="outline" colorPalette="teal" leftIcon={<FaPlus fontSize="12px" />} onClick={handleAddNewFile}>
                Add File
              </Button>

              <Button
                variant="solid"
                onClick={handleRun}
                isDisabled={
                  fileItems.length < 1 || !fields.trim() || !fileItems.some((item) => item.file.size > 0)
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
                  transform="translate(-50%, -50%)"
                  zIndex="1"
                >
                  <Spinner size="lg" color="blue.500" />
                </Box>
              )}
              {results ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                  {results}
                </ReactMarkdown>
              ) : (
                <Text color="gray.500">Results will appear here after running.</Text>
              )}
            </Box>
          </VStack>
        ) : (
            // New table-based Batch Mode UI with Chakra UI v3 syntax
          <VStack spacing={4} align="stretch">
            <Box overflowX="auto" width="100%">
              <Table.Root variant="simple" width="100%">
                <Table.Header>
                  <Table.Row>
                    <Table.ColumnHeader width="100px">Files</Table.ColumnHeader>
                    {batchFileItems.map((batchItem, index) => (
                      <Table.ColumnHeader key={index} textAlign="center">
                        <ColumnHeaderUploader 
                          index={index}
                          isHandwritten={batchItem.isHandwritten}
                          onAddFiles={(newFiles) => {
                            // Update the files in this column
                            const updatedBatchItems = [...batchFileItems];
                            updatedBatchItems[index] = {
                              ...updatedBatchItems[index],
                              files: [...updatedBatchItems[index].files, ...newFiles]
                            };
                            setBatchFileItems(updatedBatchItems);
                          }}
                          onRemove={() => removeBatchUploader(index)}
                          onToggleHandwritten={() => toggleBatchHandwritten(index)}
                          isRemoveDisabled={batchFileItems.length <= 1}
                        />
                      </Table.ColumnHeader>
                    ))}
                    <Table.ColumnHeader width="60px">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        colorPalette="teal" 
                        leftIcon={<FaPlus fontSize="10px" />}
                        onClick={addBatchUploader}
                      >
                        Add Source
                      </Button>
                    </Table.ColumnHeader>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {/* Find the maximum number of files in any column */}
                  {Array.from({ length: Math.max(1, ...batchFileItems.map(item => item.files.length)) }).map((_, rowIndex) => (
                    <Table.Row key={rowIndex}>
                      <Table.Cell fontWeight="medium">File {rowIndex + 1}</Table.Cell>
                      
                      {/* Map through each column */}
                      {batchFileItems.map((batchItem, colIndex) => (
                        <Table.Cell key={colIndex} padding={2}>
                          {rowIndex < batchItem.files.length ? (
                            // Display file if it exists for this row/column
                            <VStack width="100%" spacing={0}>
                              <HStack width="100%" mb={2}>
                                <Box 
                                  border="1px solid" 
                                  borderColor="gray.200" 
                                  borderRadius="md" 
                                  p={2} 
                                  bg="white"
                                  width="100%"
                                  height="36px"
                                  overflow="hidden"
                                >
                                  <Box
                                    maxW="100%"
                                    maxH="32px"
                                    overflowY="auto"
                                    overflowX="hidden"
                                    css={{
                                      '&::-webkit-scrollbar': { width: '4px' },
                                      '&::-webkit-scrollbar-track': { width: '6px', background: 'transparent' },
                                      '&::-webkit-scrollbar-thumb': { background: '#CBD5E0', borderRadius: '24px' },
                                    }}
                                    title={batchItem.files[rowIndex].name}
                                    textAlign="left"
                                    display="flex"
                                    alignItems="flex-start"
                                    justifyContent="flex-start"
                                    lineHeight="tight"
                                    fontSize="sm"
                                  >
                                    {batchItem.files[rowIndex].name}
                                  </Box>
                                </Box>
                                <Box>
                                  <Button 
                                    size="xs" 
                                    colorPalette="red" 
                                    onClick={() => removeFileFromBatchUploader(colIndex, rowIndex)}
                                  >
                                    ✕
                                  </Button>
                                </Box>
                              </HStack>
                              
                              {/* Only display the reorder button if this is not the last file 
                                  right above an empty row */}
                              {rowIndex < batchItem.files.length - 1 && (
                                <Button
                                  size="xs"
                                  colorPalette="blue"
                                  variant="ghost"
                                  width="100%"
                                  height="20px"
                                  onClick={() => {
                                    // Open a reorder dialog or initiate a draggable interaction
                                    // For now, we'll create a simple toggle between up and down
                                    const isFirstFile = rowIndex === 0;
                                    const isLastFile = rowIndex === batchItem.files.length - 1;
                                    
                                    // If it's the first file, we can only move down
                                    if (isFirstFile) {
                                      moveFileInColumn(colIndex, rowIndex, 'down');
                                    }
                                    // If it's the last file, we can only move up
                                    else if (isLastFile) {
                                      moveFileInColumn(colIndex, rowIndex, 'up');
                                    }
                                    // For files in the middle, we'll toggle between moving up and down
                                    else {
                                      // Using a simple approach - move up first, then next click will move down
                                      // This could be improved with a proper UI
                                      const direction = rowIndex % 2 === 0 ? 'up' : 'down';
                                      moveFileInColumn(colIndex, rowIndex, direction);
                                    }
                                  }}
                                >
                                  <Box display="flex" flexDirection="column" alignItems="center" fontSize="10px" lineHeight="1">
                                    <span>↑</span>
                                    <span>↓</span>
                                  </Box>
                                </Button>
                              )}
                            </VStack>
                          ) : (
                            // Show file upload interface for empty cells
                            <FileCellUploader 
                              onAddFile={(file) => {
                                const newFiles = [...file];
                                addFilesToBatchUploader(colIndex, newFiles);
                              }} 
                            />
                          )}
                        </Table.Cell>
                      ))}
                      <Table.Cell></Table.Cell>
                    </Table.Row>
                  ))}
                  
                  {/* Add new file row */}
                  <Table.Row>
                    <Table.Cell fontWeight="medium">
                      <Text>Add Row</Text>
                    </Table.Cell>
                    {batchFileItems.map((_, colIndex) => (
                      <Table.Cell key={colIndex}>
                        <FileCellUploader 
                          onAddFile={(file) => {
                            const newFiles = [...file];
                            addFilesToBatchUploader(colIndex, newFiles);
                          }} 
                        />
                      </Table.Cell>
                    ))}
                    <Table.Cell></Table.Cell>
                  </Table.Row>
                </Table.Body>
              </Table.Root>
            </Box>

            <HStack spacing={4}>
              <Button 
                variant="solid"
                colorPalette={isBatchConfigValid() ? "blue" : "gray"}
                onClick={handleProcessBatch}
                isLoading={batchLoading}
                isDisabled={!isBatchConfigValid()}
              >
                {isBatchConfigValid() 
                  ? `Process ${getBatchSetCount()} Batch Sets` 
                  : "Invalid Batch Configuration"}
              </Button>
            </HStack>

            {/* Results section */}
            <Separator my={4} />
            <Heading size="md" mb={4}>Results</Heading>
            <Box>
              {batchResults.length > 0 ? (
                <Field label="Batch Set">
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
                        Batch Set {index + 1}
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
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {batchResults[selectedBatchResult]}
                    </ReactMarkdown>
                  ) : (
                    <Text color="gray.500">Results will appear here after processing batch files.</Text>
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
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
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
            <ChakraFieldRoot display="flex" alignItems="center" width="auto">
              <ChakraFieldLabel htmlFor={`handwritten-${index}`} mb="0" fontSize="sm">
                Analyze handwriting
              </ChakraFieldLabel>
              <Switch.Root id={`handwritten-${index}`} colorPalette="blue">
                <Switch.HiddenInput 
                  checked={isHandwritten} 
                  onChange={() => onToggleHandwritten(index)} 
                />
                <Switch.Control>
                  <Switch.Thumb />
                </Switch.Control>
              </Switch.Root>
            </ChakraFieldRoot>
            
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


// Add this component right below your BatchFileDropzone component 
const FileCellUploader = ({ onAddFile }: { onAddFile: (files: File[]) => void }) => {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onAddFile(acceptedFiles);
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    multiple: false, // Only allow one file per drop for this cell
  });

  return (
    <VStack width="100%" spacing={0} height="62px"> {/* Match the height of a file cell with its reorder button */}
      <Box 
        {...getRootProps()} 
        border="1px dashed" 
        borderColor="gray.300" 
        borderRadius="md" 
        p={2}
        textAlign="center"
        cursor="pointer"
        _hover={{ borderColor: "blue.500", bg: "blue.50" }}
        height="36px"
        width="100%"
        fontSize="sm"
        display="flex"
        alignItems="center"
        justifyContent="center"
        mb={2} /* Match the mb={2} from the HStack in the file display */
      >
        <input {...getInputProps()} />
        <Text fontSize="xs" color="gray.500">
          Drop file or click
        </Text>
      </Box>
      {/* Add invisible spacing element to match the reorder button's height */}
      <Box height="20px" width="100%"></Box>
    </VStack>
  );
};

// Add this new component for the column header uploader

const ColumnHeaderUploader = ({ 
  index, 
  isHandwritten, 
  onAddFiles, 
  onRemove, 
  onToggleHandwritten,
  isRemoveDisabled
}: { 
  index: number, 
  isHandwritten: boolean,
  onAddFiles: (files: File[]) => void,
  onRemove: () => void, 
  onToggleHandwritten: () => void,
  isRemoveDisabled: boolean
}) => {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onAddFiles(acceptedFiles);
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    multiple: true, // Allow multiple files
  });

  return (
    <VStack>
      <Box 
        {...getRootProps()} 
        width="100%"
        textAlign="center"
        cursor="pointer"
        borderRadius="md"
        p={1}
        _hover={{ bg: "blue.50" }}
      >
        <input {...getInputProps()} />
        <Text fontSize="sm">Source {index + 1}</Text>
        <Text fontSize="xs" color="blue.500">Click to upload multiple files</Text>
      </Box>
      
      <HStack>
        <ChakraField.Root display="flex" alignItems="center" width="auto">
          <ChakraField.Label htmlFor={`batch-handwritten-${index}`} mb="0" fontSize="xs">
            Analyze Handwriting
          </ChakraField.Label>
          <Switch.Root id={`batch-handwritten-${index}`} colorPalette="blue" size="sm">
            <Switch.HiddenInput 
              checked={isHandwritten} 
              onChange={onToggleHandwritten} 
            />
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
          </Switch.Root>
        </ChakraField.Root>
        
        <Button 
          size="xs" 
          colorPalette="red" 
          onClick={onRemove}
          isDisabled={isRemoveDisabled}
        >
          ✕
        </Button>
      </HStack>
    </VStack>
  );
};

const BatchFileDropzone = ({
  index,
  files,
  isHandwritten,
  onAddFiles,
  onRemoveFile,
  onRemoveUploader,
  onReorderFiles,
  onToggleHandwritten,
}: {
  index: number;
  files: File[];
  isHandwritten: boolean;
  onAddFiles: (newFiles: File[]) => void;
  onRemoveFile: (fileIndex: number) => void;
  onRemoveUploader: () => void;
  onReorderFiles: (newFiles: File[]) => void;
  onToggleHandwritten: () => void;
}) => {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onAddFiles(acceptedFiles);
      }
    },
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    multiple: true, // Allow multiple files
  });

  // Define handleDragEnd inside the component
  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    
    const reorderedFiles = Array.from(files);
    const [movedFile] = reorderedFiles.splice(result.source.index, 1);
    reorderedFiles.splice(result.destination.index, 0, movedFile);
    onReorderFiles(reorderedFiles);
  };

  // Create safe IDs without special characters
  const getSafeId = (fileIndex: number) => `file-${index}-${fileIndex}`;

  return (
    <Box
      position="relative"
      border="2px dashed"
      borderColor="gray.300"
      borderRadius="md"
      p={4}
      minW="250px" // Ensure a fixed or minimum width
      maxW="300px"
      flex="1" // Allow flexibility in the horizontal layout
    >
      <VStack align="stretch" spacing={2}>
        {/* Header with handwriting toggle */}
        <HStack justify="space-between" mb={1}>
          <VStack align="start" spacing={0}>
            <Text fontWeight="bold">Source {index + 1}</Text>
            {files.length > 0 && (
              <Text fontSize="xs" color="gray.600">
                {files.length} {files.length === 1 ? "file" : "files"} for processing
              </Text>
            )}
          </VStack>
          <ChakraField.Root display="flex" alignItems="center" width="auto">
            <ChakraField.Label htmlFor={`batch-handwritten-${index}`} mb="0" fontSize="sm">
              Analyze handwriting
            </ChakraField.Label>
            <Switch.Root id={`batch-handwritten-${index}`} colorPalette="blue">
              <Switch.HiddenInput 
                checked={isHandwritten} 
                onChange={onToggleHandwritten} 
              />
              <Switch.Control>
                <Switch.Thumb />
              </Switch.Control>
            </Switch.Root>
          </ChakraField.Root>
        </HStack>

        <Box {...getRootProps()} textAlign="center" cursor="pointer" _hover={{ borderColor: "blue.500" }}>
          <input {...getInputProps()} />
          <Text>Drag and drop files here, or click to browse</Text>
        </Box>

        {/* Display uploaded files */}
        {files.length > 0 && (
          <Box>
            <Text fontWeight="bold" mb={2}>
              Uploaded Files:
            </Text>
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId={`batch-${index}`}>
                {(provided) => (
                  <VStack
                    align="stretch"
                    spacing={1}
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                  >
                    {files.map((file, fileIndex) => (
                      <Draggable
                        key={getSafeId(fileIndex)}
                        draggableId={getSafeId(fileIndex)}
                        index={fileIndex}
                      >
                        {(provided) => (
                          <HStack
                            justify="space-between"
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            mb={1}
                            bg="white"
                            p={2}
                            borderRadius="md"
                            border="1px solid"
                            borderColor="gray.200"
                            height="30px" // Fixed height
                            overflow="hidden" // Prevent overflow
                            width="100%"
                          >
                            <Box
                              maxW="60%"
                              maxH="32px"
                              overflowY="auto"
                              overflowX="hidden"
                              css={{
                                '&::-webkit-scrollbar': {
                                  width: '4px',
                                },
                                '&::-webkit-scrollbar-track': {
                                  width: '6px',
                                  background: 'transparent',
                                },
                                '&::-webkit-scrollbar-thumb': {
                                  background: '#CBD5E0',
                                  borderRadius: '24px',
                                },
                              }}
                              title={file.name}
                              textAlign="left"
                              display="flex"
                              alignItems="flex-start"
                              justifyContent="flex-start"
                              lineHeight="tight"
                              fontSize="sm"
                              p={0}
                            >
                              {file.name}
                            </Box>
                            <HStack spacing={2}>
                              {/* Move Up Button */}
                              <Button
                                size="xs"
                                colorScheme="blue"
                                onClick={() => {
                                  if (fileIndex > 0) {
                                    const reorderedFiles = Array.from(files);
                                    const [movedFile] = reorderedFiles.splice(fileIndex, 1);
                                    reorderedFiles.splice(fileIndex - 1, 0, movedFile);
                                    onReorderFiles(reorderedFiles);
                                  }
                                }}
                                isDisabled={fileIndex === 0}
                                flexShrink={0}
                                minW="24px" // Fixed minimum width
                                height="24px" // Fixed height
                              >
                                ↑
                              </Button>

                              {/* Move Down Button */}
                              <Button
                                size="xs"
                                colorScheme="blue"
                                onClick={() => {
                                  if (fileIndex < files.length - 1) {
                                    const reorderedFiles = Array.from(files);
                                    const [movedFile] = reorderedFiles.splice(fileIndex, 1);
                                    reorderedFiles.splice(fileIndex + 1, 0, movedFile);
                                    onReorderFiles(reorderedFiles);
                                  }
                                }}
                                isDisabled={fileIndex === files.length - 1}
                                flexShrink={0}
                                minW="24px" // Fixed minimum width
                                height="24px" // Fixed height
                              >
                                ↓
                              </Button>

                              {/* Remove File Button */}
                              <Button
                                size="xs"
                                colorScheme="red"
                                onClick={() => onRemoveFile(fileIndex)}
                                flexShrink={0}
                                minW="24px" // Fixed minimum width
                                height="24px" // Fixed height
                              >
                                Remove
                              </Button>
                            </HStack>
                          </HStack>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </VStack>
                )}
              </Droppable>
            </DragDropContext>
          </Box>
        )}

        {/* Remove uploader button */}
        <Button size="sm" colorScheme="red" onClick={onRemoveUploader}>
          Remove Uploader
        </Button>
      </VStack>
    </Box>
  );
};

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/formconnect")({
  component: FormConnect,
})