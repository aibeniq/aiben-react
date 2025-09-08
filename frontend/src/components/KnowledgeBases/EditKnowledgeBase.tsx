import {
  Box,
  Button,
  ButtonGroup,
  DialogActionTrigger,
  HStack,
  Input,
  Link,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useDropzone } from "react-dropzone"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt, FaTrash } from "react-icons/fa"

import {
  type ApiError,
  type KnowledgeBasePublic,
  KnowledgeBasesService,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import SourceLink from "../Common/SourceLink"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditKnowledgeBaseProps {
  item: KnowledgeBasePublic
}

interface KnowledgeBaseUpdateForm {
  title: string
  description?: string
}

const EditKnowledgeBase = ({ item }: EditKnowledgeBaseProps) => {
  console.log("KnowledgeBase item:", item)
  console.log("KnowledgeBase item ID:", item.id)

  const [isOpen, setIsOpen] = useState(false)
  const [formIsValid, setFormIsValid] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [removedFileIds, setRemovedFileIds] = useState<string[]>([])
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: knowledgeBase } = useQuery({
    queryKey: ["knowledge-base", item.id],
    queryFn: async () => {
      console.log("Fetching knowledge base with ID:", item.id)
      const result = await KnowledgeBasesService.readKnowledgeBase({
        id: item.id,
      })
      console.log("📊 Knowledge base API response:", result)
      console.log("📊 Embedding model ID:", result.embedding_model_id)
      return result
    },
    enabled: isOpen, // Only fetch when dialog is open
  })

  const validateForm = () => {
    // Check if title is valid and there's at least one file (existing or new)
    const hasTitleValue = !!knowledgeBase?.title
    const hasExistingFiles =
      knowledgeBase?.files &&
      knowledgeBase.files.filter((f: any) => !removedFileIds.includes(f.id))
        .length > 0
    const hasNewFiles = selectedFiles.length > 0
    const hasFiles = hasExistingFiles || hasNewFiles

    return hasTitleValue && hasFiles
  }

  useEffect(() => {
    setFormIsValid(validateForm())
  }, [knowledgeBase, selectedFiles, removedFileIds])

  console.log("KnowledgeBase data:", knowledgeBase)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<KnowledgeBaseUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    // Initialize with item prop instead
    defaultValues: {
      title: item.title,
      description: item.description ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: async (
      data: KnowledgeBaseUpdateForm & {
        files: File[]
        removedFileIds: string[]
      },
    ) => {
      console.log("Now beginning mutation...")

      const payload = {
        title: data.title,
        description: data.description,
        id: item.id,
        // Preserve the existing embedding model ID
        embeddingModelId:
          knowledgeBase?.embedding_model_id || item.embedding_model_id,
        formData: {
          files: data.files,
          ...(data.removedFileIds && data.removedFileIds.length > 0
            ? { removed_file_ids: data.removedFileIds }
            : { removed_file_ids: ["00000000-0000-0000-0000-000000000000"] }), // sending a dummy entry if no deletions
        },
      }

      console.log(
        "Payload being sent to KnowledgeBasesService.updateKnowledgeBase:",
        payload,
      )
      console.log("Preserving embedding_model_id:", payload.embeddingModelId)

      return KnowledgeBasesService.updateKnowledgeBase(payload)
    },
    onSuccess: () => {
      showSuccessToast("Knowledge Base updated successfully.")
      setIsOpen(false)
      // Force immediate cache invalidation and refetch
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
      queryClient.refetchQueries({ queryKey: ["items"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      // Additional invalidation on settlement
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
  })

  const onSubmit: SubmitHandler<KnowledgeBaseUpdateForm> = async (data) => {
    console.log("Submitting form data:", data)
    console.log("Selected files:", selectedFiles)
    console.log("Removed file IDs:", removedFileIds)

    console.log("Form submitted, isSubmitting:", isSubmitting)

    const hasExistingFiles =
      knowledgeBase?.files &&
      knowledgeBase.files.filter((f: any) => !removedFileIds.includes(f.id))
        .length > 0
    const hasNewFiles = selectedFiles.length > 0

    if (!hasExistingFiles && !hasNewFiles) {
      showErrorToast("At least one file is required.")
      return
    }

    mutation.mutate({
      ...data,
      files: selectedFiles,
      removedFileIds,
    })
  }

  const onDrop = (acceptedFiles: File[]) => {
    setSelectedFiles((prev) => [...prev, ...acceptedFiles])
  }

  const handleRemoveNewFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleRemoveExistingFile = (fileId: string) => {
    setRemovedFileIds((prev) => [...prev, fileId])
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/plain": [".txt"],
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/rtf": [".rtf"],
    },
    multiple: true,
  })

  // Add useEffect to update form when knowledgeBase data loads
  useEffect(() => {
    if (knowledgeBase) {
      reset({
        title: knowledgeBase.title,
        description: knowledgeBase.description ?? undefined,
      })
    }
  }, [knowledgeBase, reset])

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit Knowledge Base
        </Button>
      </DialogTrigger>
      <DialogContent>
        <Box position="relative">
          {/* Add spinner and grey overlay when submitting */}
          {mutation.isPending && (
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
              <Spinner size="xl" />
            </Box>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Edit Knowledge Base</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Text mb={4}>Update the Knowledge Base details below.</Text>
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
                      required: "Title is required",
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

                {/* Existing Files */}
                {knowledgeBase?.files && knowledgeBase.files.length > 0 && (
                  <Box w="full">
                    <Text mb={2}>Current Files:</Text>
                    <VStack align="start" gap={2}>
                      {knowledgeBase.files
                        .filter(
                          (file: any) => !removedFileIds.includes(file.id),
                        )
                        .map((file: any) => (
                          <HStack
                            key={file.id}
                            w="full"
                            justify="space-between"
                          >
                            {/* Use SourceLink component for on-demand loading */}
                            <SourceLink
                              sourceId={file.id}
                              fileName={file.name}
                              useModal={true}
                            />
                            <Box
                              as="button"
                              aria-label="Remove file"
                              onClick={() => handleRemoveExistingFile(file.id)}
                              _hover={{ color: "red.500" }}
                            >
                              <FaTrash />
                            </Box>
                          </HStack>
                        ))}
                    </VStack>
                  </Box>
                )}

                {/* File Upload Area */}
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
                  <Text>
                    {isDragActive
                      ? "Drop the files here..."
                      : "Drag and drop files here, or click to browse"}
                  </Text>
                </Box>

                {/* New Selected Files */}
                {selectedFiles.length > 0 && (
                  <Box w="full">
                    <Text mb={2}>New Files:</Text>
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
                            onClick={() => handleRemoveNewFile(index)}
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
              <ButtonGroup>
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
                  disabled={!formIsValid || isSubmitting}
                  loading={isSubmitting}
                >
                  {isSubmitting ? "Saving..." : "Save"}
                </Button>
              </ButtonGroup>
            </DialogFooter>
          </form>
        </Box>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditKnowledgeBase
