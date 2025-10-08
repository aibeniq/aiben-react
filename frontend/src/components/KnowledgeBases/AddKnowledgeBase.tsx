import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useRef, useState } from "react"
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
  Progress,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useTranslation } from "react-i18next"
import { FaPlus, FaTrash } from "react-icons/fa"

import { EmbeddingModelsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { useKnowledgeBaseProgress } from "@/hooks/useKnowledgeBaseProgress"
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
import { Tooltip } from "../ui/tooltip"

interface KnowledgeBaseCreate {
  title: string
  description: string
}

const AddKnowledgeBase = () => {
  const { t, ready } = useTranslation()

  // Helper function to truncate text with ellipsis
  const truncateText = (text: string, maxLength = 60): string => {
    if (text.length <= maxLength) return text
    return `${text.substring(0, maxLength)}...`
  }

  const [isOpen, setIsOpen] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]) // State for managing selected files
  const [selectedEmbeddingModelId, setSelectedEmbeddingModelId] = useState<
    string | null
  >(null)
  const [availableProviders, setAvailableProviders] = useState<string[]>([]) //only show Embedding Model providers allowed in config.py
  const [taskId, setTaskId] = useState<string | null>(null)
  const hasHandledCompletionRef = useRef(false) // Prevent multiple success toasts

  // Progress state from the backend
  const progress = useKnowledgeBaseProgress(taskId)

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

  // Handle progress completion and close modal
  useEffect(() => {
    console.log("🔍 Completion handler check:", {
      taskId,
      "progress.completed": progress.completed,
      "progress.error": progress.error,
      "hasHandledCompletionRef.current": hasHandledCompletionRef.current,
      "progress.percentage": progress.percentage,
      "progress.isActive": progress.isActive,
    })

    // CRITICAL FIX: Only handle completion if we have an active task AND reasonable progress
    // This prevents cached completion state from immediately triggering success on modal reopen
    if (
      taskId &&
      progress.completed &&
      !progress.error &&
      !hasHandledCompletionRef.current &&
      progress.percentage > 80
    ) {
      // Ensure we actually made meaningful progress
      console.log(
        "✅ Knowledge base creation completed successfully - handling completion for task:",
        taskId,
      )

      // Mark completion as handled to prevent multiple toasts
      hasHandledCompletionRef.current = true

      // Show success toast only when entire process is complete
      showSuccessToast(t("knowledgeBases.modals.messages.createSuccess"))

      // Invalidate queries to refresh the list with the new knowledge base
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
      queryClient.refetchQueries({ queryKey: ["items"] })

      // Close modal and reset task ID
      setIsOpen(false)
      setTaskId(null)
    } else if (taskId && progress.error && !hasHandledCompletionRef.current) {
      console.error("❌ Knowledge base creation failed:", progress.error)
      hasHandledCompletionRef.current = true
      showErrorToast(progress.error)
      setTaskId(null)
    }
  }, [
    taskId,
    progress.completed,
    progress.error,
    showErrorToast,
    showSuccessToast,
    queryClient,
    t,
  ])

  // Reset completion handler whenever taskId changes (new task starts)
  useEffect(() => {
    if (taskId) {
      console.log(
        "🔄 New task started:",
        taskId,
        "- resetting completion handler",
      )
      hasHandledCompletionRef.current = false
    }
  }, [taskId])

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
      setTaskId(null)
      hasHandledCompletionRef.current = false // Reset completion handler for next time

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
    } else {
      // CRITICAL FIX: Modal is opening - aggressively reset ALL state
      console.log(
        "🔓 Modal is opening - AGGRESSIVELY resetting ALL state to prevent cached completion",
      )
      setTaskId(null)
      hasHandledCompletionRef.current = false

      // Force immediate state reset to prevent any cached progress from previous session
      setTimeout(() => {
        console.log(
          "🧹 AGGRESSIVE CLEANUP: Ensuring all state is reset after modal open",
        )
        setTaskId(null)
        hasHandledCompletionRef.current = false
      }, 50)
    }
  }, [isOpen, reset, queryClient])

  const mutation = useMutation({
    mutationFn: async (data: {
      title: string
      description: string
      embedding_model_id: string | null
      files: File[]
    }) => {
      console.log("🚀 Starting knowledge base creation mutation")

      // Basic validation - ensure we have files
      if (data.files.length === 0) {
        throw new Error("Please select at least one file to upload")
      }

      const totalSize = data.files.reduce((sum, file) => sum + file.size, 0)
      console.log(
        `📊 Upload stats: ${data.files.length} files, ${(totalSize / (1024 * 1024)).toFixed(1)}MB total`,
      )

      // Step 1: Create task first to get task_id immediately using OpenAPI client
      console.log("🎯 Step 1: Creating task first to get immediate task_id...")

      // Import OpenAPI client dynamically to avoid circular dependencies
      const { OpenAPI } = await import("@/client/core/OpenAPI")
      const { request } = await import("@/client/core/request")

      const taskPromise = request(OpenAPI, {
        method: "POST",
        url: "/api/v1/knowledge-bases/create-task",
        query: {
          title: data.title,
          description: data.description,
          embedding_model_id: data.embedding_model_id,
        },
      })

      const taskData = (await taskPromise) as { task_id: string }

      console.log("✅ Got task_id immediately:", taskData.task_id)

      // Return task_id immediately so progress tracking can start
      return { task_id: taskData.task_id }
    },
    onSuccess: async (data, variables) => {
      console.log("✅ Task creation SUCCESS - got task_id immediately:", data)

      // Check for task_id and log the response structure
      console.log("🔍 Response structure:", Object.keys(data))
      console.log("🔍 Full response data:", data)

      if (data.task_id) {
        console.log("✅ Found task_id in response:", data.task_id)

        // CRITICAL FIX: Reset completion handler BEFORE setting new task ID to prevent race conditions
        hasHandledCompletionRef.current = false

        // SAFETY: Ensure no stale task ID exists before setting new one
        setTaskId(null)

        // Small delay to ensure state is fully reset before setting new task ID
        setTimeout(() => {
          console.log("🎯 Setting new Task ID after reset:", data.task_id)
          setTaskId(data.task_id)
          console.log(
            "🎯 Task ID set to:",
            data.task_id,
            "- progress polling should now be active",
          )
        }, 100)

        // Step 2: Start the actual file upload in the background
        console.log("🚀 Step 2: Starting file upload in background...")

        // CRITICAL FIX: Use setTimeout to ensure the upload starts after the component re-render
        // This prevents the mutation completion from interfering with progress polling
        setTimeout(async () => {
          try {
            const { createKnowledgeBaseWithTimeout } = await import(
              "@/client/knowledgeBaseClient"
            )
            console.log("📤 Starting file upload with task_id:", data.task_id)

            const uploadResult = await createKnowledgeBaseWithTimeout({
              title: variables.title,
              description: variables.description,
              embeddingModelId: variables.embedding_model_id,
              formData: {
                files: variables.files,
              },
              taskId: data.task_id, // Pass the task_id
            })
            console.log(
              "✅ File upload POST completed successfully:",
              uploadResult,
            )
            console.log(
              "🔄 Background processing should now continue with task_id:",
              data.task_id,
            )
            console.log(
              "⚠️ Frontend should KEEP POLLING until task reaches 100%",
            )

            // CRITICAL: Ensure the taskId remains set even after POST completes
            // The background processing will continue and update progress via the same task_id
            console.log(
              "🎯 Ensuring taskId remains set for continued polling:",
              data.task_id,
            )
          } catch (err) {
            console.error("❌ File upload failed:", err)
            // Error will be shown via progress tracker
          }
        }, 100) // Small delay to let the component re-render complete
      } else {
        console.error(
          "❌ No task_id in response. Response keys:",
          Object.keys(data),
        )
        console.error("❌ Full response object:", data)
      }

      // Note: Success toast and modal close will happen when progress reaches completion
      // This onSuccess only means the task was created and file upload started
    },
    onError: (err: any) => {
      console.error("❌ Knowledge base creation ERROR:", err)

      let errorMessage = "Failed to create knowledge base"

      if (err.message?.includes("Too many files")) {
        errorMessage = err.message
      } else if (err.status === 409) {
        errorMessage =
          (err.body as { detail: string }).detail ||
          "A knowledge base with this title already exists"
      } else if (
        err.message?.includes("Network Error") ||
        err.code === "ERR_NETWORK"
      ) {
        errorMessage =
          "Upload timeout or server error. Try with fewer/smaller files or check your connection."
      } else if (err.body?.detail) {
        errorMessage = err.body.detail
      }

      showErrorToast(errorMessage)

      // Reset task ID on error
      setTaskId(null)
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
    console.log("🔍 isSubmitting at start:", isSubmitting)

    if (selectedFiles.length === 0) {
      console.log("⚠️ No files selected - showing error")
      showErrorToast(t("knowledgeBases.modals.add.validation.atLeastOneFile"))
      return
    }

    console.log(
      "📁 Selected files:",
      selectedFiles.map((f) => f.name),
    )

    // For large uploads, inform user about async processing
    const fileCount = selectedFiles.length
    const totalSizeMB =
      selectedFiles.reduce((sum, file) => sum + file.size, 0) / (1024 * 1024)

    if (fileCount > 100 || totalSizeMB > 100) {
      console.log(
        `⚠️ Large upload detected: ${fileCount} files, ${totalSizeMB.toFixed(1)}MB`,
      )
      // Could add a confirmation dialog here in the future
    }

    // Prepare the data for the SDK function
    const requestData = {
      title: data.title,
      description: data.description || "",
      embedding_model_id: selectedEmbeddingModelId,
      files: selectedFiles, // Pass the selected files
    }

    console.log("📤 Prepared request data:", {
      ...requestData,
      files: `${requestData.files.length} files`,
    })

    try {
      console.log("🚀 Calling mutation.mutateAsync...")
      console.log("🔍 isSubmitting before mutation:", isSubmitting)
      await mutation.mutateAsync(requestData)
      console.log("✅ Mutation completed successfully")
      console.log("🔍 isSubmitting after mutation:", isSubmitting)
      // The success handling is now in the mutation's onSuccess callback
    } catch (error) {
      // Error handling is in the mutation's onError callback
      console.error("❌ Mutation failed:", error)
      console.log("🔍 isSubmitting after error:", isSubmitting)
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
      "text/csv": [".csv"], // CSV files
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ], // Excel files (modern format)
      "application/vnd.ms-excel": [".xls"], // Excel files (legacy format)
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
          {t("knowledgeBases.addKnowledgeBase")}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <Box position="relative">
          {(isSubmitting ||
            progress.isActive ||
            (taskId && !progress.completed)) && (
            <Box
              position="absolute"
              top="0"
              left="0"
              right="0"
              bottom="0"
              bg="blackAlpha.800"
              zIndex="50"
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              borderRadius="md"
              p={6}
            >
              <VStack gap={4} width="80%" maxWidth="400px">
                <Text
                  color="white"
                  fontSize="lg"
                  fontWeight="medium"
                  textAlign="center"
                >
                  {progress.message ||
                    t("knowledgeBases.modals.messages.processing")}
                </Text>
                <Box width="100%">
                  <Progress.Root
                    value={progress.percentage}
                    size="lg"
                    colorPalette="blue"
                  >
                    <Progress.Track>
                      <Progress.Range />
                    </Progress.Track>
                  </Progress.Root>
                  <Text color="white" fontSize="sm" textAlign="center" mt={2}>
                    {Math.round(progress.percentage)}%
                  </Text>
                </Box>
                <Text color="gray.300" fontSize="sm" textAlign="center">
                  {ready
                    ? t("knowledgeBases.modals.messages.pleaseWait")
                    : "Please wait while we create your knowledge base"}
                </Text>
              </VStack>
            </Box>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>{t("knowledgeBases.modals.add.title")}</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Text mb={4}>{t("knowledgeBases.modals.add.description")}</Text>
              <VStack gap={4}>
                <Field
                  required
                  invalid={!!errors.title}
                  errorText={errors.title?.message}
                  label={t("knowledgeBases.modals.fields.title")}
                >
                  <Input
                    id="title"
                    {...register("title", {
                      required: t(
                        "knowledgeBases.modals.validation.titleRequired",
                      ),
                    })}
                    placeholder={t("knowledgeBases.modals.fields.title")}
                    type="text"
                  />
                </Field>

                <Field
                  invalid={!!errors.description}
                  errorText={errors.description?.message}
                  label={t("knowledgeBases.modals.fields.description")}
                >
                  <Input
                    id="description"
                    {...register("description")}
                    placeholder={t("knowledgeBases.modals.fields.description")}
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
                    <Text>
                      {t("knowledgeBases.modals.fileUpload.dropFiles")}
                    </Text>
                  ) : (
                    <Text>
                      {t("knowledgeBases.modals.fileUpload.dragAndDrop")}
                    </Text>
                  )}
                </Box>

                {/* File Upload Limits Info */}
                <Box fontSize="sm" color="gray.600" textAlign="center" px={2}>
                  <Box>
                    <Text fontSize="xs" color="gray.500">
                      {t("knowledgeBases.modals.fileUpload.supportedFormats")}
                    </Text>
                  </Box>
                </Box>

                {/* Display Selected Files */}
                {selectedFiles.length > 0 && (
                  <Box w="full">
                    <Text mb={2}>
                      {t("knowledgeBases.modals.fileUpload.selectedFiles")}
                    </Text>
                    <VStack align="start" gap={2}>
                      {selectedFiles.map((file, index) => {
                        const truncatedName = truncateText(file.name)
                        const needsTooltip = file.name.length > 30

                        return (
                          <HStack
                            key={index}
                            w="full"
                            justify="space-between"
                            minW="0"
                          >
                            <Box flex="1" minW="0">
                              {needsTooltip ? (
                                <Tooltip content={file.name} showArrow>
                                  <Link
                                    href={URL.createObjectURL(file)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    color="blue.500"
                                    _hover={{ textDecoration: "underline" }}
                                  >
                                    {truncatedName}
                                  </Link>
                                </Tooltip>
                              ) : (
                                <Link
                                  href={URL.createObjectURL(file)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  color="blue.500"
                                  _hover={{ textDecoration: "underline" }}
                                >
                                  {file.name}
                                </Link>
                              )}
                            </Box>
                            <Box
                              as="button"
                              aria-label={t(
                                "knowledgeBases.modals.fileUpload.removeFile",
                              )}
                              onClick={() => handleRemoveFile(index)}
                              _hover={{ color: "red.500" }}
                              flexShrink={0}
                            >
                              <FaTrash />
                            </Box>
                          </HStack>
                        )
                      })}
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
                  {t("knowledgeBases.modals.buttons.cancel")}
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
                {isSubmitting
                  ? t("knowledgeBases.modals.buttons.creating")
                  : t("knowledgeBases.modals.buttons.create")}
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
