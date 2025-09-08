import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useDropzone } from "react-dropzone"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Box,
  Button,
  DialogActionTrigger,
  DialogTitle,
  HStack,
  Input,
  Link,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { FaPlus, FaTrash } from "react-icons/fa"

import { EmbeddingModelsService, KnowledgeBasesService } from "@/client"
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
  const [selectedEmbeddingModelId, setSelectedEmbeddingModelId] = useState<
    string | null
  >(null)
  const [availableProviders, setAvailableProviders] = useState<string[]>([]) //only show Embedding Model providers allowed in config.py
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
    queryFn: () =>
      EmbeddingModelsService.getEmbeddingModels().then((res) => res.data),
    // Don't fetch if modal is closed
    enabled: isOpen,
  })

  const { data: defaultModel } = useQuery({
    queryKey: ["default-embedding-model"],
    queryFn: () => EmbeddingModelsService.getDefaultEmbeddingModel(),
    enabled: isOpen,
  })

  // determine which embedding models are allowed
  useEffect(() => {
    EmbeddingModelsService.getAvailableProviders()
      .then((response) => {
        if (
          response.embedding_providers &&
          Array.isArray(response.embedding_providers)
        ) {
          setAvailableProviders(response.embedding_providers)
        } else {
          setAvailableProviders(["openai", "aws"]) // fallback
        }
      })
      .catch(() => setAvailableProviders(["openai", "aws"]))
  }, [])

  const filteredEmbeddingModels = embeddingModels.filter(
    (model) => model.provider && availableProviders.includes(model.provider),
  )

  // Set the default embedding model when the component mounts
  useEffect(() => {
    if (
      isOpen &&
      !selectedEmbeddingModelId && // Only set if not already selected
      (defaultModel?.id || filteredEmbeddingModels?.length > 0)
    ) {
      if (defaultModel?.id) {
        setSelectedEmbeddingModelId(defaultModel.id)
      } else if (
        filteredEmbeddingModels?.length > 0 &&
        filteredEmbeddingModels[0]?.id
      ) {
        setSelectedEmbeddingModelId(filteredEmbeddingModels[0].id)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, defaultModel, filteredEmbeddingModels])

  // Reset selected files when the popup is closed
  useEffect(() => {
    console.log("📱 Modal state changed - isOpen:", isOpen)
    if (!isOpen) {
      console.log("🔒 Modal is closing - resetting form and files")
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

      // Force a final cache refresh when modal closes
      console.log("🔄 Final cache invalidation on modal close...")
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
      console.log("✅ Modal close cleanup completed")
    }
  }, [isOpen, reset, queryClient])

  const mutation = useMutation({
    mutationFn: (data: {
      title: string
      description: string
      embedding_model_id: string | null
      files: File[]
    }) => {
      console.log(
        "🚀 Starting knowledge base creation mutation with data:",
        data,
      )

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
    onSuccess: (data) => {
      console.log("✅ Knowledge base creation SUCCESS:", data)
      showSuccessToast("Knowledge Base created successfully.")
      setIsOpen(false)

      // Invalidate BOTH query keys
      console.log("🔄 Invalidating knowledge-bases cache...")
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })

      console.log(
        "🔄 Invalidating items cache (the one actually used by the list)...",
      )
      queryClient.invalidateQueries({ queryKey: ["items"] })

      console.log("🔄 Forcing refetch of items...")
      queryClient.refetchQueries({ queryKey: ["items"] })

      console.log("✨ Knowledge base creation success flow completed")
    },
    onError: (err: ApiError) => {
      console.error("❌ Knowledge base creation ERROR:", err)
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
      console.log(
        "🏁 Knowledge base mutation SETTLED - doing final cache invalidation",
      )
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
  })

  const onSubmit: SubmitHandler<KnowledgeBaseCreate> = async (data) => {
    console.log("📝 Form submitted with data:", data)

    if (selectedFiles.length === 0) {
      console.log("⚠️ No files selected - showing error")
      showErrorToast("At least one file is required.")
      return
    }

    console.log(
      "📁 Selected files:",
      selectedFiles.map((f) => f.name),
    )

    // Prepare the data for the SDK function
    const requestData = {
      title: data.title,
      description: data.description || "",
      embedding_model_id: selectedEmbeddingModelId,
      files: selectedFiles, // Pass the selected files
    }

    console.log("📤 Prepared request data:", requestData)

    try {
      console.log("🚀 Calling mutation.mutateAsync...")
      await mutation.mutateAsync(requestData)
      console.log("✅ Mutation completed successfully")
      // The success handling is now in the mutation's onSuccess callback
    } catch (error) {
      // Error handling is in the mutation's onError callback
      console.error("❌ Mutation failed:", error)
    }
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
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"], // Word documents (modern format)
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
        <Button
          variant="solid"
          color="white"
          bg="rgba(0, 65, 72, 0.9)"
          _hover={{
            bg: "rgba(0, 65, 72, 0.85)",
          }}
          value="add-item"
          my={4}
        >
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
              <Spinner color="blue.500" size="xl" />
            </Box>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Add Knowledge Base</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Text mb={4}>
                Fill in the details to add a new Knowledge Base.
              </Text>
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

                {/* Comment out or remove this entire Field block to hide the embedding model dropdown */}
                {/*
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
                    {filteredEmbeddingModels.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name} ({model.provider}){" "}
                        {defaultModel?.id === model.id ? "(Default)" : ""}
                      </option>
                    ))}
                  </select>
                </Field>
                */}

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
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button
                variant="solid"
                color="white"
                bg="rgba(0, 65, 72, 0.9)"
                _hover={{
                  bg: "rgba(0, 65, 72, 0.85)",
                }}
                type="submit"
                disabled={!isValid || isSubmitting}
              >
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
