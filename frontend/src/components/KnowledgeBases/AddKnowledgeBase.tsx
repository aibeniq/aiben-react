import { useMutation, useQueryClient } from "@tanstack/react-query"
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
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus, FaTrash } from "react-icons/fa"

import { type KnowledgeBaseCreate, KnowledgeBasesService } from "@/client"
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

const AddKnowledgeBase = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]) // State for managing selected files
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<KnowledgeBaseCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      description: "",
    },
  })

  const mutation = useMutation({
  mutationFn: (data: { title: string; description: string; files: File[] }) => {
    //console.log("Now beginning mutation...");

    // Construct the FormData object
    const formData = new FormData();

    // Append files to the FormData object
    data.files.forEach((file) => {
      formData.append("files", file);
    });

    // Append title and description to the FormData object
    //formData.append("title", data.title);
    //formData.append("description", data.description);

    //console.log("FormData being sent:", formData);

    // Send the FormData object to the backend
    return KnowledgeBasesService.createKnowledgeBase({
      title: data.title, // Still required for the `query` object
      description: data.description, // Still required for the `query` object
      requestBody: formData, // Include all fields in the FormData payload
    });
  },
  onSuccess: () => {
    showSuccessToast("Knowledge Base created successfully.");
    reset();
    setSelectedFiles([]); // Reset selected files after successful creation
    setIsOpen(false);
  },
  onError: (err: ApiError) => {
    handleError(err);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] });
  },
});


  const onSubmit: SubmitHandler<KnowledgeBaseCreate> = (data) => {
    if (selectedFiles.length === 0) {
      showErrorToast("At least one file is required.")
      return
    }
    
    // Prepare the data for the SDK function
    const requestData = {
      title: data.title,
      description: data.description || "",
      files: selectedFiles, // Pass the selected files
    }

    console.log([requestData])

    mutation.mutate(requestData)
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
                  <VStack align="start" spacing={2}>
                    {selectedFiles.map((file, index) => (
                      <HStack key={index} w="full" justify="space-between">
                        <Text isTruncated>{file.name}</Text>
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
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddKnowledgeBase
