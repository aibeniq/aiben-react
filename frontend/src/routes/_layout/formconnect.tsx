import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  Textarea,
  VStack,
  HStack,
} from "@chakra-ui/react"
import { useState, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import { FormconnectService } from "@/client"

const FormConnect = () => {
  const [files, setFiles] = useState<File[]>([])
  const [fields, setFields] = useState("")
  const [results, setResults] = useState("")

  const mutation = useMutation({
    mutationFn: (data: {fields: string; files: File[]}) => {
      console.log("Now beginning mutation...")
      
      return FormconnectService.processForm({
        fields: data.fields,
        formData: {
          files: data.files,
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
    setFiles(prevFiles => [...prevFiles, file])
  }

  const removeFile = (index: number) => {
    setFiles(prevFiles => prevFiles.filter((_, i) => i !== index))
  }

  const updateFile = (index: number, file: File) => {
    setFiles(prevFiles => prevFiles.map((f, i) => i === index ? file : f))
  }

  const handleAddNewFile = () => {
    // This will add a placeholder that will be replaced when the user selects a file
    addFile(new File([], "placeholder"))
  }

  const handleRun = async () => {
    if (files.length < 1) {
      setResults("Please upload at least one file.")
      return
    }

    if (!fields.trim()) {
      setResults("Please enter at least one field.")
      return
    }

    // Filter out placeholder files (if any)
    const validFiles = files.filter(f => f.size > 0)

    const requestData = {
      fields: fields,
      files: validFiles,
    }
    console.log("Request Data:", requestData)

    mutation.mutate(requestData)
  }

  // Add to your component (place in FormConnect before the return statement)
  useEffect(() => {
    // Start with one empty file slot
    if (files.length === 0) {
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
        {files.map((file, index) => (
          <FileDropzone 
            key={index}
            index={index}
            file={file}
            onUpdate={updateFile}
            onRemove={removeFile}
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
          isDisabled={files.length < 1 || !fields.trim()}
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

// FileDropzone component definition here
const FileDropzone = ({ index, file, onUpdate, onRemove }: { 
  index: number, 
  file: File | null, 
  onUpdate: (index: number, file: File) => void,
  onRemove: (index: number) => void 
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
    },
    multiple: false,
  })

  // Check if file is a placeholder (empty file with name "placeholder")
  const isPlaceholder = file && file.name === "placeholder" && file.size === 0

  return (
    <Box position="relative">
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
      {file && (
        <Button 
          size="sm" 
          colorScheme="red" 
          position="absolute" 
          top="5px" 
          right="5px"
          onClick={(e) => {
            e.stopPropagation()
            onRemove(index)
          }}
        >
          ✕
        </Button>
      )}
    </Box>
  )
}

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/formconnect")({
  component: FormConnect,
})