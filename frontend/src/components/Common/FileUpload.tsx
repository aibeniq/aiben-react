import {
  Box,
  Button,
  Text,
  VStack,
  HStack,
  Switch,
  Field as ChakraField,
  Card,
  Heading,
} from "@chakra-ui/react"
import { useDropzone } from "react-dropzone"
import { FiUpload, FiFile, FiCheck } from "react-icons/fi"

export interface FileItem {
  file: File
  isHandwritten: boolean
}

interface FileUploadProps {
  files: FileItem[]
  onFilesChange: (files: FileItem[]) => void
  acceptedFileTypes?: Record<string, string[]>
  maxFiles?: number
  showHandwrittenToggle?: boolean
}

const defaultAcceptedTypes = {
  "application/pdf": [".pdf"],
  "text/plain": [".txt"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/gif": [".gif"],
  "image/bmp": [".bmp"],
  "image/tiff": [".tif", ".tiff"],
  "image/webp": [".webp"],
}

const FileUpload = ({
  files,
  onFilesChange,
  acceptedFileTypes = defaultAcceptedTypes,
  maxFiles,
  showHandwrittenToggle = true,
}: FileUploadProps) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const newFileItems = acceptedFiles.map((file) => ({
          file,
          isHandwritten: false,
        }))

        const updatedFiles = [...files, ...newFileItems]
        if (maxFiles && updatedFiles.length > maxFiles) {
          onFilesChange(updatedFiles.slice(0, maxFiles))
        } else {
          onFilesChange(updatedFiles)
        }
      }
    },
    accept: acceptedFileTypes,
  })

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index)
    onFilesChange(updatedFiles)
  }

  const toggleHandwritten = (index: number) => {
    const updatedFiles = files.map((item, i) =>
      i === index ? { ...item, isHandwritten: !item.isHandwritten } : item,
    )
    onFilesChange(updatedFiles)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i]
  }

  const hasFiles = files.length > 0

  return (
    <VStack align="stretch" gap={4}>
      <Card.Root
        cursor="pointer"
        _hover={{
          borderColor: isDragActive ? "blue.500" : "gray.300",
          bg: isDragActive ? "blue.50" : "gray.50",
        }}
        borderColor={isDragActive ? "blue.500" : hasFiles ? "rgba(0, 65, 72, 0.2)" : "gray.200"}
        bg={isDragActive ? "blue.50" : "surface"}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <Card.Body p={6}>
          <HStack gap={4} align="center">
            <HStack gap={3} align="center">
              <Box
                p={3}
                borderRadius="full"
                bg={hasFiles ? "rgba(0, 65, 72, 0.9)" : isDragActive ? "blue.100" : "gray.100"}
                color={hasFiles ? "white" : isDragActive ? "blue.600" : "gray.500"}
              >
                <FiUpload size={24} />
              </Box>
              <VStack gap={1} align="start">
                <Heading size="md">
                  {hasFiles
                    ? `${files.length} File${files.length > 1 ? "s" : ""} Selected`
                    : "Upload Documents"}
                </Heading>
                <Text fontSize="sm" color="gray.600">
                  {isDragActive
                    ? "Drop the files here..."
                    : "Click to add more files or drag and drop"}
                </Text>
              </VStack>
            </HStack>

            <Box color={hasFiles ? "rgba(0, 65, 72, 0.9)" : "gray.400"} ml="auto">
              {hasFiles ? <FiCheck size={16} /> : ""}
            </Box>
          </HStack>
        </Card.Body>
      </Card.Root>

      {files.length > 0 && (
        <Card.Root bg="surface">
          <Card.Body p={4}>
            <VStack align="stretch" gap={3}>
              <Text fontWeight="medium" color="gray.700">
                Uploaded Files ({files.length})
              </Text>
              <VStack align="stretch" gap={2} maxH="300px" overflowY="auto">
                {files.map((fileItem, index) => (
                  <HStack
                    key={`${fileItem.file.name}-${index}`}
                    justify="space-between"
                    bg="surface"
                    p={3}
                    borderRadius="md"
                    border="1px solid"
                    borderColor="gray.200"
                    _hover={{ borderColor: "gray.300", bg: "gray.100" }}
                  >
                    <HStack gap={3} flex="1" minW="0">
                      <Box p={2} borderRadius="md" color="rgba(0, 65, 72, 0.7)">
                        <FiFile size={16} />
                      </Box>
                      <Box flex="1" minW="0">
                        <Text fontWeight="medium" truncate>
                          {fileItem.file.name}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {formatFileSize(fileItem.file.size)}
                        </Text>
                      </Box>
                    </HStack>

                    <HStack gap={2} flexShrink={0}>
                      {showHandwrittenToggle && (
                        <ChakraField.Root display="flex" alignItems="center" width="auto">
                          <ChakraField.Label
                            htmlFor={`handwritten-${index}`}
                            mb="0"
                            fontSize="sm"
                            mr={2}
                          >
                            Handwritten
                          </ChakraField.Label>
                          <Switch.Root id={`handwritten-${index}`} colorPalette="blue">
                            <Switch.HiddenInput
                              checked={fileItem.isHandwritten}
                              onChange={() => toggleHandwritten(index)}
                            />
                            <Switch.Control>
                              <Switch.Thumb />
                            </Switch.Control>
                          </Switch.Root>
                        </ChakraField.Root>
                      )}

                      <Button
                        size="sm"
                        colorPalette="red"
                        variant="outline"
                        onClick={() => removeFile(index)}
                      >
                        Remove
                      </Button>
                    </HStack>
                  </HStack>
                ))}
              </VStack>
            </VStack>
          </Card.Body>
        </Card.Root>
      )}
    </VStack>
  )
}

export default FileUpload
