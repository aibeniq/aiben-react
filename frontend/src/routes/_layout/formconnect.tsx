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
  Field
} from "@chakra-ui/react"
import { useState, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import { FormconnectService } from "@/client"

const FormConnect = () => {
  const [fileItems, setFileItems] = useState<Array<{
    file: File;
    isHandwritten: boolean;
  }>>([]);

  const [fields, setFields] = useState("")
  const [results, setResults] = useState("")

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
      setResults("Please upload at least one file.")
      return
    }

    if (!fields.trim()) {
      setResults("Please enter at least one field.")
      return
    }

    // Filter out placeholder files and separate into digitized vs handwritten
    const validItems = fileItems.filter(item => item.file.size > 0)
    const digitizedFiles = validItems.filter(item => !item.isHandwritten).map(item => item.file)
    const handwrittenFiles = validItems.filter(item => item.isHandwritten).map(item => item.file)

    const requestData = {
      fields: fields,
      digitized_files: digitizedFiles,
      handwritten_files: handwrittenFiles,
    }

    console.log("Request Data:", requestData)

    mutation.mutate(requestData)
  }

  // Add to your component (place in FormConnect before the return statement)
  useEffect(() => {
    // Start with one empty file slot
    if (fileItems.length === 0) {
      handleAddNewFile()
    }
  }, [])

  return (
    <Container maxW="lg" py={8}>
      <Heading size="lg" mb={6}>
        FormConnect
      </Heading>
      <VStack spacing={4} align="stretch">
        {/* File Uploaders */}
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

        {/* Add File Button */}
        <Button colorScheme="teal" onClick={handleAddNewFile}>
          + Add File
        </Button>

        {/* Fields Textarea */}
        <Textarea
          placeholder="Enter fields, one per line"
          value={fields}
          onChange={(e) => setFields(e.target.value)}
          rows={6}
        />

        {/* Run Button */}
        <Button 
          colorScheme="blue" 
          onClick={handleRun}
          isDisabled={fileItems.length < 1 || !fields.trim() || !fileItems.some(item => item.file.size > 0)}
        >
          Run
        </Button>

        {/* Results Area */}
        <Box
          border="1px solid"
          borderColor="gray.300"
          borderRadius="md"
          p={4}
          bg="gray.50"
          minH="100px"
          maxH="400px"
          overflowY="auto"
        >
          <Text whiteSpace="pre-wrap">{results || "Results will appear here after running."}</Text>
        </Box>
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

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/formconnect")({
  component: FormConnect,
})