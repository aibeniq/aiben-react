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
  Field,
  Spinner,
  Input
} from "@chakra-ui/react"
import { useState, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import { FormconnectService } from "@/client"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd' 

const FormConnect = () => {
  const [mode, setMode] = useState<"manual" | "batch">("manual"); // Toggle between Manual and Batch Mode
  const [batchFileItems, setBatchFileItems] = useState<Array<{ 
    files: Array<{ file: File; isHandwritten: boolean }> 
  }>>([
    { files: [] },
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
        i === index ? { files: [...item.files, ...newFiles] } : item
      )
    );
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

  const isBatchConfigValid = () => {
    if (batchFileItems.length < 2) return false;
    
    const fileCount = batchFileItems[0].files.length;
    if (fileCount === 0) return false;
    
    return batchFileItems.every(item => item.files.length === fileCount);
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
      <Heading size="lg" mb={6}>
        FormConnect
      </Heading>
      
      <VStack spacing={4} align="stretch">
        {/* Fields Textarea */}
        <Box>
          <Text mb={2}>Forms</Text>
          <select
            value={selectedForm?.id || ""}
            onChange={(e) => {
              const form = forms.find((f) => f.id === e.target.value);
              setSelectedForm(form);
              setFields(form?.fields || "");
              setFormName(form?.name || ""); // Update formName state
              setFormDescription(form?.description || ""); // Update formDescription state
            }}
          >
            <option value="">Select a form</option>
            {forms.map((form) => (
              <option key={form.id} value={form.id}>
                {form.name}
              </option>
            ))}
          </select>

          <Box>
            <Text mb={2}>Form Name</Text>
            <Input
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="Enter form name"
            />
          </Box>
          <Box>
            <Text mb={2}>Form Description</Text>
            <Textarea
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              placeholder="Enter form description"
            />
          </Box>

          <Box>
            <Text mb={2}>Fields</Text>
            <Textarea
              value={fields}
              onChange={(e) => setFields(e.target.value)}
              placeholder="Enter fields, one per line"
              rows={6}
            />
          </Box>

          <HStack spacing={4}>
          <Button
            colorScheme="teal"
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

                  alert("Form updated successfully.");
                } else {
                  // Create a new form
                  const response = await FormconnectService.createForm({
                    requestBody: {
                      name: formName,
                      description: formDescription,
                      fields,
                    },
                  });

                  //if (!response.ok) {
                  //  throw new Error("Failed to save form");
                  //}

                  const newForm = await response
                  setForms((prev) => [...prev, newForm]);
                  alert("Form created successfully.");
                }

                // Clear the form fields and re-fetch the list of forms
                setFormName("");
                setFormDescription("");
                setFields("");
                setSelectedForm(null);
                await fetchForms();
              } catch (error) {
                console.error("Error saving form:", error);
                alert("Failed to save form. Please try again.");
              }
            }}
          >
            Save Form
          </Button>

          <Button
            colorScheme="blue"
            onClick={async () => {
              if (!selectedForm) {
                alert("Please select a form to copy.");
                return;
              }

              try {
                // Create a copy of the selected form
                const response = await FormconnectService.createForm({
                  requestBody: {
                    name: `${selectedForm.name} (Copy)`, // Append "(Copy)" to the name
                    description: selectedForm.description,
                    fields: selectedForm.fields,
                  },
                });

                //if (!response.ok) {
                //  throw new Error("Failed to copy form");
                //}

                const newForm = await response
                setForms((prev) => [...prev, newForm]);
                alert("Form copied successfully.");

                // Re-fetch the list of forms
                await fetchForms();
              } catch (error) {
                console.error("Error copying form:", error);
                alert("Failed to copy form. Please try again.");
              }
            }}
            isDisabled={!selectedForm} // Disable the button if no form is selected
          >
            Copy Form
          </Button>

          <Button
            colorScheme="red"
            onClick={async () => {
              if (!selectedForm) {
                alert("Please select a form to delete.");
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

                alert("Form deleted successfully.");
              } catch (error) {
                console.error("Error deleting form:", error);
                alert("Failed to delete form. Please try again.");
              }
            }}
            isDisabled={!selectedForm} // Disable the button if no form is selected
          >
            Delete Form
        </Button>
        </HStack>
        </Box>
        
        {/* Mode Toggle */}
        <Box>
          <HStack justify="space-between" align="center">
            <Text>Mode:</Text>
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
        </Box>

        {/* Conditional Rendering Based on Mode */}
        {mode === "manual" ? (
          <>
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

            <Button colorScheme="teal" onClick={handleAddNewFile}>
              + Add File
            </Button>

            <Button
              colorScheme="blue"
              onClick={handleRun}
              isDisabled={
                fileItems.length < 1 || !fields.trim() || !fileItems.some((item) => item.file.size > 0)
              }
            >
              Run
            </Button>

            <Box
              border="1px solid"
              borderColor="gray.300"
              borderRadius="md"
              p={4}
              bg="gray.50"
              minH="100px"
              maxH="400px"
              overflowY="auto"
              position="relative"
              opacity={loading ? 0.5 : 1} // Grey out the panel when loading
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
                <Text>Results will appear here after running.</Text>
              )}
            </Box>
          </>
        ) : (
          <>
            {/* Batch Mode UI */}
            <HStack spacing={4} align="start" wrap="wrap" width="100%">
            {batchFileItems.map((batchItem, index) => (
              <BatchFileDropzone
                key={index}
                index={index}
                files={batchItem.files}
                onAddFiles={(newFiles) => addFilesToBatchUploader(index, newFiles)}
                onRemoveFile={(fileIndex) => removeFileFromBatchUploader(index, fileIndex)}
                onRemoveUploader={() => removeBatchUploader(index)}
                onReorderFiles={(newFiles) => reorderFilesInBatchUploader(index, newFiles)}
                onToggleHandwritten={() => toggleBatchHandwritten(index)}
              />
            ))}
            </HStack>

            <HStack spacing={4} mt={4}>
            <Button colorScheme="teal" onClick={addBatchUploader}>
              + Add Uploader
            </Button>

            <Button 
              colorScheme={isBatchConfigValid() ? "blue" : "gray"}
              onClick={handleProcessBatch}
              isLoading={batchLoading}
              isDisabled={!isBatchConfigValid()}
            >
              {isBatchConfigValid() 
                ? `Process ${batchFileItems[0].files.length} Batch Sets` 
                : "Invalid Batch Configuration"}
            </Button>

            {/* Batch results section */}
            {batchResults.length > 0 && (
              <Box>
                <HStack spacing={4} mb={2}>
                  <Text>Results:</Text>
                  <select
                    value={selectedBatchResult}
                    onChange={(e) => setSelectedBatchResult(Number(e.target.value))}
                    style={{ padding: '0.5rem', borderRadius: '0.375rem' }}
                  >
                    {batchResults.map((_, index) => (
                      <option key={index} value={index}>
                        Batch Set {index + 1}
                      </option>
                    ))}
                  </select>
                </HStack>
                
                <Box
                  border="1px solid"
                  borderColor="gray.300"
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
                      <Text>No results available.</Text>
                    )
                  )}
                </Box>
              </Box>
            )}
          </HStack>
          </>
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
            <Field.Root display="flex" alignItems="center" width="auto">
              <Field.Label htmlFor={`handwritten-${index}`} mb="0" fontSize="sm">
                Analyze handwriting
              </Field.Label>
              <Switch.Root id={`handwritten-${index}`} colorPalette="blue">
                <Switch.HiddenInput 
                  checked={isHandwritten} 
                  onChange={() => onToggleHandwritten(index)} 
                />
                <Switch.Control>
                  <Switch.Thumb />
                </Switch.Control>
              </Switch.Root>
            </Field.Root>
            
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
          <Field.Root display="flex" alignItems="center" width="auto">
            <Field.Label htmlFor={`batch-handwritten-${index}`} mb="0" fontSize="sm">
              Analyze handwriting
            </Field.Label>
            <Switch.Root id={`batch-handwritten-${index}`} colorPalette="blue">
              <Switch.HiddenInput 
                checked={isHandwritten} 
                onChange={onToggleHandwritten} 
              />
              <Switch.Control>
                <Switch.Thumb />
              </Switch.Control>
            </Switch.Root>
          </Field.Root>
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
                          >
                            <Text>{file.name}</Text>
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
                              >
                                ↓
                              </Button>

                              {/* Remove File Button */}
                              <Button
                                size="xs"
                                colorScheme="red"
                                onClick={() => onRemoveFile(fileIndex)}
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