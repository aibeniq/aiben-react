import {
  Box,
  Button,
  Container,
  Heading,
  Input,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { useDropzone } from "react-dropzone"
import { createFileRoute } from "@tanstack/react-router"

import { useMutation } from "@tanstack/react-query";
import { FormconnectService, FormconnectProcessFormData } from "@/client"


const FormConnect = () => {
  const [file1, setFile1] = useState<File | null>(null)
  const [file2, setFile2] = useState<File | null>(null)
  const [fields, setFields] = useState("")
  const [results, setResults] = useState("")

  const mutation = useMutation({
    mutationFn: (data: {fields: string; files: File[]}) => {
      console.log("Now beginning mutation...");
      
      // Send the FormData object to the backend
      return FormconnectService.processForm({
        fields: data.fields, // Still required for the `query` object
        formData: {
          files: data.files, // ✅ this is what the SDK expects
        }, // Include all fields in the FormData payload
      });
    },
    onSuccess: (data) => {
      setResults(data.results);
    },
    onError: (error) => {
      console.log("Mutation unsuccessful!")
      setResults(`Error: ${error.message}`);
    },
  })

  const handleFileDrop = (acceptedFiles: File[], setFile: (file: File) => void) => {
    console.log("Handling dropped file...")
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
    }
  }

  const { getRootProps: getFile1Props, getInputProps: getFile1InputProps } = useDropzone({
    onDrop: (acceptedFiles) => handleFileDrop(acceptedFiles, setFile1),
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    multiple: false,
  })

  const { getRootProps: getFile2Props, getInputProps: getFile2InputProps } = useDropzone({
    onDrop: (acceptedFiles) => handleFileDrop(acceptedFiles, setFile2),
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    multiple: false,
  })


  const handleRun = async () => {
    console.log("File 1:")
    console.log(file1)

    console.log("File 2:")
    console.log(file2)
    
    if (!file1 || !file2) {
        setResults("Please upload both File 1 and File 2.")
        return
    }

    if (!fields.trim()) {
        setResults("Please enter at least one field.")
        return
    }

    const filesList = [file1, file2];

    // Prepare the data for the SDK function
    const requestData = {
      fields: fields,
      files: filesList, // Pass the selected files
    }
    console.log("Request Data:")
    console.log(requestData)

    mutation.mutate(requestData);

    // Construct the payload as a plain object
    //const payload = {
    //  file1, // File object
    //  file2, // File object
    //  fields, // String
    //};

    //mutation.mutate({payload});
    console.log("Mutation triggered")

    }

  return (
    <Container maxW="lg" py={8}>
      <Heading size="lg" mb={6}>
        FormConnect
      </Heading>
      <VStack spacing={4} align="stretch">
        {/* File 1 Uploader */}
        <Box
          {...getFile1Props()}
          border="2px dashed"
          borderColor="gray.300"
          borderRadius="md"
          p={4}
          textAlign="center"
          cursor="pointer"
          _hover={{ borderColor: "blue.500" }}
        >
          <input {...getFile1InputProps()} />
          <Text>{file1 ? `Selected File: ${file1.name}` : "Drag and drop File 1 here, or click to browse"}</Text>
        </Box>

        {/* File 2 Uploader */}
        <Box
          {...getFile2Props()}
          border="2px dashed"
          borderColor="gray.300"
          borderRadius="md"
          p={4}
          textAlign="center"
          cursor="pointer"
          _hover={{ borderColor: "blue.500" }}
        >
          <input {...getFile2InputProps()} />
          <Text>{file2 ? `Selected File: ${file2.name}` : "Drag and drop File 2 here, or click to browse"}</Text>
        </Box>

        {/* Fields Textarea */}
        <Textarea
          placeholder="Enter fields, one per line"
          value={fields}
          onChange={(e) => setFields(e.target.value)}
          rows={6}
        />

        {/* Run Button */}
        <Button colorScheme="blue" onClick={handleRun}>
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
        >
          <Text whiteSpace="pre-wrap">{results || "Results will appear here after running."}</Text>
        </Box>
      </VStack>
    </Container>
  )
}

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/formconnect")({
  component: FormConnect,
})