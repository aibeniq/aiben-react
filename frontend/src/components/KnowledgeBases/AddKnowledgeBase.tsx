import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useDropzone } from "react-dropzone"

import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
  HStack,
  Box,
  Spinner,
  Link,
} from "@chakra-ui/react"
import { useState, useEffect } from "react"
import { FaPlus, FaTrash } from "react-icons/fa"

import { type KnowledgeBaseCreate, KnowledgeBasesService, EmbeddingModelsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface KnowledgeBaseCreate {
  title: string
  description: string
}

const AddKnowledgeBase = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]) // State for managing selected files
  const [selectedEmbeddingModelId, setSelectedEmbeddingModelId] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<KnowledgeBaseCreate>({
    mode: "onSubmit",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      description: "",
    },
  })

  const { data: embeddingModels = [] } = useQuery({
    queryKey: ["embedding-models"],
    queryFn: () => EmbeddingModelsService.getEmbeddingModels().then((res) => res.data),
    // Don't fetch if modal is closed
    enabled: isOpen,
  })

  // Set the default embedding model when the component mounts
  useEffect(() => {
    if (embeddingModels?.length > 0) {
      // Find the default model
      const defaultModel = embeddingModels.find((model) => model.is_default)

      // If a default model exists, use its ID, otherwise use the first model's ID
      if (defaultModel) {
        setSelectedEmbeddingModelId(defaultModel.id)
      } else if (embeddingModels[0]) {
        setSelectedEmbeddingModelId(embeddingModels[0].id)
      }
    }
  }, [embeddingModels])

  // Reset selected files when the popup is closed
  useEffect(() => {
    if (!isOpen) {
      setSelectedFiles([])
      setSelectedEmbeddingModelId(null)

      // Also reset the form completely, including errors
      reset(
        {
          title: "",
          description: "",
        },
        {
          keepErrors: false, // This clears all errors
          keepDirty: false, // This resets dirty state
          keepTouched: false, // This resets touched state
        },
      )
    }
  }, [isOpen])

  const mutation = useMutation({
    mutationFn: (data: {
      title: string
      description: string
      embedding_model_id: string | null
      files: File[]
    }) => {
      console.log("Now beginning mutation...")

      // Send the FormData object to the backend
      return KnowledgeBasesService.createKnowledgeBase({
        title: data.title, // Still required for the `query` object
        description: data.description, // Still required for the `query` object
        embeddingModelId: data.embedding_model_id,
        formData: {
          files: data.files, // ✅ this is what the SDK expects
        }, // Include all fields in the FormData payload
      })
    },
    onSuccess: () => {
      showSuccessToast("Knowledge Base created successfully.")
      reset()
      setSelectedFiles([]) // Reset selected files after successful creation
      setSelectedEmbeddingModelId(null)
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      if (err.status === 409) {
        // Handle duplicate title error specifically
        showErrorToast(
          (err.body as { detail: string }).detail ||
            "A knowledge base with this title already exists",
        )
      } else {
        // Handle other errors
        handleError(err)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
    },
  })

  const onSubmit: SubmitHandler<KnowledgeBaseCreate> = (data) => {
    if (selectedFiles.length === 0) {
      showErrorToast("At least one file is required.")
      return
    }

    // Prepare the data for the SDK function
    const requestData = {
      title: data.title,
      description: data.description || "",
      embedding_model_id: selectedEmbeddingModelId,
      files: selectedFiles, // Pass the selected files
    }

    console.log([requestData])

    return mutation.mutateAsync(requestData)
  }

  const onDrop = (acceptedFiles: File[]) => {
    setSelectedFiles((prevFiles) => [...prevFiles, ...acceptedFiles]) // Add new files to the existing list
  }

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index))
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected: (fileRejections) => {
      fileRejections.forEach((file) => {
        showErrorToast(`File ${file.file.name} is not supported.`)
        console.error(`File ${file.file.name} is not supported.`)
      })
    },
    accept: {
      "text/plain": [".txt"], // Plain text files
      "application/pdf": [".pdf"], // PDF files
      "application/msword": [".doc"], // Word documents
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"], // Word documents (modern format)
      "application/rtf": [".rtf"], // Rich Text Format files
    },
    multiple: true, // Allow multiple file uploads
  })

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-item" my={4}>
          <FaPlus fontSize="16px" />
          Add Knowledge Base
        </Button>
      </DialogTrigger>
      <DialogContent>
        <Box position="relative">
          {isSubmitting && (
            <Box
              position="absolute"
              top="0"
              left="0"
              right="0"
              bottom="0"
              bg="blackAlpha.300"
              zIndex="50"
              display="flex"
              alignItems="center"
              justifyContent="center"
              borderRadius="md"
            >
              <Spinner
                thickness="4px"
                speed="0.65s"
                emptyColor="gray.200"
                color="blue.500"
                size="xl"
              />
            </Box>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Add Knowledge Base</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Text mb={4}>Fill in the details to add a new Knowledge Base.</Text>
              <VStack gap={4}>
                <Field
                  required
                  invalid={!!errors.title}
                  errorText={errors.title?.message}
                  label="Title"
                >
                  <Input
                    id="title"
                    {...register("title", {
                      required: "Title is required.",
                    })}
                    placeholder="Title"
                    type="text"
                  />
                </Field>

                <Field
                  invalid={!!errors.description}
                  errorText={errors.description?.message}
                  label="Description"
                >
                  <Input
                    id="description"
                    {...register("description")}
                    placeholder="Description"
                    type="text"
                  />
                </Field>

                <Field label="Embedding Model">
                  <select
                    value={selectedEmbeddingModelId || ""}
                    onChange={(e) => setSelectedEmbeddingModelId(e.target.value || null)}
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      borderRadius: "0.375rem",
                      borderColor: "#E2E8F0",
                    }}
                  >
                    {embeddingModels.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name} ({model.provider}) {model.is_default ? "(Default)" : ""}
                      </option>
                    ))}
                  </select>
                </Field>

                {/* Drag-and-Drop File Upload */}
                <Box
                  {...getRootProps()}
                  border="2px dashed"
                  borderColor={isDragActive ? "blue.500" : "gray.300"}
                  borderRadius="md"
                  p={4}
                  textAlign="center"
                  cursor="pointer"
                  _hover={{ borderColor: "blue.500" }}
                >
                  <input {...getInputProps()} />
                  {isDragActive ? (
                    <Text>Drop the files here...</Text>
                  ) : (
                    <Text>Drag and drop files here, or click to browse</Text>
                  )}
                </Box>

                {/* Display Selected Files */}
                {selectedFiles.length > 0 && (
                  <Box w="full">
                    <Text mb={2}>Selected Files:</Text>
                    <VStack align="start" gap={2}>
                      {selectedFiles.map((file, index) => (
                        <HStack key={index} w="full" justify="space-between">
                          <Link
                            href={URL.createObjectURL(file)}
                            target="_blank"
                            rel="noopener noreferrer"
                            color="blue.500"
                            _hover={{ textDecoration: "underline" }}
                          >
                            {file.name}
                          </Link>
                          <Box
                            as="button"
                            aria-label="Remove file"
                            onClick={() => handleRemoveFile(index)}
                            _hover={{ color: "red.500" }}
                          >
                            <FaTrash />
                          </Box>
                        </HStack>
                      ))}
                    </VStack>
                  </Box>
                )}
              </VStack>
            </DialogBody>

            <DialogFooter gap={2}>
              <DialogActionTrigger asChild>
                <Button variant="subtle" colorPalette="gray" disabled={isSubmitting}>
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" disabled={!isValid || isSubmitting}>
                {isSubmitting ? "Creating..." : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </Box>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddKnowledgeBase
