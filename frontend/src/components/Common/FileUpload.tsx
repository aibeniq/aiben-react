import { Box, Button, Text, VStack, HStack, Switch, Field as ChakraField } from "@chakra-ui/react"
import { useDropzone } from "react-dropzone"

export interface FileItem {
  file: File
  isHandwritten: boolean
}

interface FileUploadProps {
  files: FileItem[]
  onFilesChange: (files: FileItem[]) => void
  multiple?: boolean
  acceptedFileTypes?: Record<string, string[]>
  maxFiles?: number
  placeholder?: string
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
  multiple = true,
  acceptedFileTypes = defaultAcceptedTypes,
  maxFiles,
  placeholder = "Drag and drop files here, or click to browse",
  showHandwrittenToggle = true,
}: FileUploadProps) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const newFileItems = acceptedFiles.map((file) => ({
          file,
          isHandwritten: false,
        }))

        if (multiple) {
          const updatedFiles = [...files, ...newFileItems]
          if (maxFiles && updatedFiles.length > maxFiles) {
            onFilesChange(updatedFiles.slice(0, maxFiles))
          } else {
            onFilesChange(updatedFiles)
          }
        } else {
          onFilesChange([newFileItems[0]])
        }
      }
    },
    accept: acceptedFileTypes,
    multiple,
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

  return (
    <VStack align="stretch" gap={4}>
      {/* File Upload Area */}
      <Box
        border="2px dashed"
        borderColor={isDragActive ? "blue.500" : "gray.300"}
        borderRadius="md"
        p={6}
        textAlign="center"
        cursor="pointer"
        bg={isDragActive ? "blue.50" : "transparent"}
        _hover={{ borderColor: "blue.500", bg: "blue.50" }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <VStack gap={2}>
          <Text fontWeight="medium">{isDragActive ? "Drop the files here..." : placeholder}</Text>
          <Text fontSize="sm" color="gray.500">
            {multiple
              ? `You can upload multiple files${maxFiles ? ` (max ${maxFiles})` : ""}`
              : "Upload a single file"}
          </Text>
          {Object.keys(acceptedFileTypes).length > 0 && (
            <Text fontSize="xs" color="gray.400">
              Supported formats: {Object.values(acceptedFileTypes).flat().join(", ")}
            </Text>
          )}
        </VStack>
      </Box>

      {/* Uploaded Files List */}
      {files.length > 0 && (
        <Box>
          <Text fontWeight="medium" mb={3}>
            Uploaded Files ({files.length})
          </Text>
          <VStack align="stretch" gap={2} maxH="300px" overflowY="auto">
            {files.map((fileItem, index) => (
              <HStack
                key={`${fileItem.file.name}-${index}`}
                justify="space-between"
                bg="white"
                p={3}
                borderRadius="md"
                border="1px solid"
                borderColor="gray.200"
                _hover={{ borderColor: "gray.300" }}
              >
                <Box flex="1" minW="0">
                  <Text fontWeight="medium" truncate>
                    {fileItem.file.name}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {formatFileSize(fileItem.file.size)}
                  </Text>
                </Box>

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
        </Box>
      )}
    </VStack>
  )
}

export default FileUpload
