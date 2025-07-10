import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
  Badge,
  Box,
  Textarea,
  Text,
  Input,
  Card,
  HStack,
} from "@chakra-ui/react"
import { useDropzone } from "react-dropzone"
import { FiUpload, FiImage, FiX, FiShield } from "react-icons/fi"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiMessageSquare, FiPlus } from "react-icons/fi"
import { z } from "zod"
import { useState } from "react"
import { useForm, type SubmitHandler } from "react-hook-form"

import { FeedbackService } from "@/client"
import type { FeedbackType, FeedbackStatus } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import useAuth from "@/hooks/useAuth"

import { Button } from "@/components/ui/button"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination"

// feedback type labels for display
const getFeedbackTypeLabel = (type: FeedbackType) => {
  switch (type) {
    case "feature_request":
      return "Feature Request"
    case "bug_report":
      return "Bug Report"
    case "general_feedback":
      return "General Feedback"
    case "improvement_suggestion":
      return "Improvement Suggestion"
    case "other":
      return "Other"
    default:
      return type
  }
}

const getStatusColor = (status: FeedbackStatus) => {
  switch (status) {
    case "open":
      return "blue"
    case "in_progress":
      return "orange"
    case "resolved":
      return "green"
    case "closed":
      return "gray"
    default:
      return "gray"
  }
}

const feedbackSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getFeedbackQueryOptions({ page, isAdmin = false }: { page: number; isAdmin?: boolean }) {
  return {
    queryFn: () =>
      isAdmin
        ? FeedbackService.getAllFeedbacksAdmin({
            skip: (page - 1) * PER_PAGE,
            limit: PER_PAGE,
          })
        : FeedbackService.getFeedbacks({
            skip: (page - 1) * PER_PAGE,
            limit: PER_PAGE,
          }),
    queryKey: ["feedback", { page, isAdmin }],
  }
}

// feedback submission form interface
interface FeedbackFormData {
  title: string
  description: string
  feedback_type: FeedbackType
}

// admin feedback update form interface
interface AdminFeedbackFormData {
  status: FeedbackStatus
  admin_notes: string
}

// image upload component for feedback
function ImageUpload({
  images,
  onImagesChange,
}: {
  images: File[]
  onImagesChange: (images: File[]) => void
}) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const imageFiles = acceptedFiles.filter((file) => file.type.startsWith("image/"))
      const updatedImages = [...images, ...imageFiles]
      onImagesChange(updatedImages)
    },
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif", ".webp"],
    },
    maxFiles: 5,
    maxSize: 5 * 1024 * 1024, // 5MB per image
  })

  const removeImage = (index: number) => {
    const updatedImages = images.filter((_, i) => i !== index)
    onImagesChange(updatedImages)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i]
  }

  return (
    <VStack align="stretch" gap={3}>
      <Card.Root
        cursor="pointer"
        _hover={{
          borderColor: isDragActive ? "blue.500" : "gray.300",
          bg: isDragActive ? "blue.50" : "gray.subtle",
        }}
        borderColor={
          isDragActive ? "blue.500" : images.length > 0 ? "rgba(0, 65, 72, 0.2)" : "gray.200"
        }
        bg={isDragActive ? "blue.50" : "surface"}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <Card.Body p={4}>
          <HStack gap={3} align="center">
            <Box
              p={2}
              borderRadius="full"
              bg={
                images.length > 0 ? "rgba(0, 65, 72, 0.9)" : isDragActive ? "blue.100" : "gray.100"
              }
              color={images.length > 0 ? "white" : isDragActive ? "blue.600" : "gray.500"}
            >
              <FiUpload size={20} />
            </Box>
            <VStack gap={1} align="start" flex="1">
              <Text fontWeight="medium" fontSize="sm">
                {images.length > 0
                  ? `${images.length} Image${images.length > 1 ? "s" : ""} Selected`
                  : "Add Images (Optional)"}
              </Text>
              <Text fontSize="xs" color="gray.600">
                {isDragActive
                  ? "Drop images here..."
                  : "Click to add images or drag and drop (max 5 images, 5MB each)"}
              </Text>
            </VStack>
          </HStack>
        </Card.Body>
      </Card.Root>

      {images.length > 0 && (
        <VStack align="stretch" gap={2} maxH="200px" overflowY="auto">
          {images.map((image, index) => (
            <HStack
              key={`${image.name}-${index}`}
              justify="space-between"
              bg="surface"
              p={3}
              borderRadius="md"
              border="1px solid"
              borderColor="gray.200"
            >
              <HStack gap={3} flex="1" minW="0">
                <Box p={2} borderRadius="md" color="rgba(0, 65, 72, 0.7)">
                  <FiImage size={16} />
                </Box>
                <Box flex="1" minW="0">
                  <Text fontWeight="medium" fontSize="sm" truncate>
                    {image.name}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {formatFileSize(image.size)}
                  </Text>
                </Box>
              </HStack>
              <Button
                size="sm"
                variant="ghost"
                colorPalette="red"
                onClick={() => removeImage(index)}
              >
                <FiX size={16} />
              </Button>
            </HStack>
          ))}
        </VStack>
      )}
    </VStack>
  )
}

// admin feedback update component
function AdminFeedbackUpdate({
  feedbackId,
  currentStatus,
  currentNotes,
}: {
  feedbackId: string
  currentStatus?: FeedbackStatus
  currentNotes?: string | null
}) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const {
    register,
    handleSubmit,
    formState: { errors, isValid, isSubmitting },
  } = useForm<AdminFeedbackFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      status: currentStatus || "open",
      admin_notes: currentNotes || "",
    },
  })

  const onSubmit: SubmitHandler<AdminFeedbackFormData> = async (data) => {
    try {
      await FeedbackService.updateFeedbackAdmin({
        feedbackId: feedbackId,
        requestBody: {
          status: data.status,
          admin_notes: data.admin_notes.trim() || null,
        },
      })

      showSuccessToast("Feedback updated successfully!")
      setIsOpen(false)

      // invalidate feedback query to refresh the list
      queryClient.invalidateQueries({ queryKey: ["feedback"] })
    } catch (error) {
      console.error("Error updating feedback:", error)
      showErrorToast("Failed to update feedback. Please try again.")
    }
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          Update
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Update Feedback</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.status}
                errorText={errors.status?.message}
                label="Status"
              >
                <select
                  id="status"
                  {...register("status", {
                    required: "Status is required.",
                  })}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #e2e8f0",
                    borderRadius: "6px",
                    fontSize: "14px",
                  }}
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </Field>

              <Field
                invalid={!!errors.admin_notes}
                errorText={errors.admin_notes?.message}
                label="Admin Notes"
              >
                <Textarea
                  id="admin_notes"
                  {...register("admin_notes", {
                    maxLength: {
                      value: 2000,
                      message: "Admin notes must be less than 2000 characters.",
                    },
                  })}
                  placeholder="Add admin notes or response..."
                  rows={4}
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button variant="subtle" colorPalette="gray" disabled={isSubmitting}>
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button variant="solid" type="submit" disabled={!isValid} loading={isSubmitting}>
              Update Feedback
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

// feedback images viewer component
function FeedbackImagesViewer({
  feedbackId,
  imageCount,
}: {
  feedbackId: string
  imageCount: number
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [images, setImages] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [imageLoading, setImageLoading] = useState(false)
  const { showErrorToast } = useCustomToast()

  const loadImages = async () => {
    if (imageCount === 0) return

    setIsLoading(true)
    try {
      const imageList = await FeedbackService.getFeedbackImages({
        feedbackId: feedbackId,
      })
      setImages(imageList)
    } catch (error) {
      console.error("Error loading images:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleOpen = () => {
    setIsOpen(true)
    if (images.length === 0) {
      loadImages()
    }
  }

  const handleViewImage = async (imageId: string) => {
    try {
      setImageLoading(true)
      // Get the access token from localStorage
      const token = localStorage.getItem("access_token")
      if (!token) {
        throw new Error("No access token found")
      }

      // Use the same API base URL as the OpenAPI configuration
      const apiBaseUrl = import.meta.env.VITE_API_URL || ""
      const imageUrl = `${apiBaseUrl}/api/v1/feedback/${feedbackId}/images/${imageId}`

      // Make a direct fetch request to get the image
      const response = await fetch(imageUrl, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Get the content type from response headers
      const contentType = response.headers.get("content-type")

      // If we're getting HTML instead of an image, throw an error
      if (contentType && contentType.includes("text/html")) {
        throw new Error("Received HTML response instead of image data")
      }

      // Get the raw binary data as an array buffer
      const arrayBuffer = await response.arrayBuffer()

      // Create a blob from the array buffer with the correct content type
      const imageBlob = new Blob([arrayBuffer], { type: contentType || "image/jpeg" })

      // Create a blob URL
      const blobUrl = URL.createObjectURL(imageBlob)

      // Set the selected image URL
      setSelectedImage(blobUrl)
    } catch (error) {
      console.error("Error viewing image:", error)
      showErrorToast("Failed to load image. Please try again.")
    } finally {
      setImageLoading(false)
    }
  }

  const closeImage = () => {
    if (selectedImage) {
      // Revoke the blob URL to free memory
      URL.revokeObjectURL(selectedImage)
      setSelectedImage(null)
    }
  }

  return (
    <>
      <DialogRoot
        size={{ base: "xs", md: "lg" }}
        placement="center"
        open={isOpen}
        onOpenChange={({ open }) => {
          setIsOpen(open)
          if (!open) {
            closeImage()
          }
        }}
      >
        <DialogTrigger asChild>
          <Button size="sm" variant="ghost" onClick={handleOpen}>
            <FiImage size={16} />
            {imageCount} image{imageCount !== 1 ? "s" : ""}
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Feedback Images</DialogTitle>
          </DialogHeader>
          <DialogBody>
            {isLoading ? (
              <VStack gap={4} py={8}>
                <Text>Loading images...</Text>
              </VStack>
            ) : images.length === 0 ? (
              <VStack gap={4} py={8}>
                <Text>No images found</Text>
              </VStack>
            ) : (
              <VStack gap={4} maxH="400px" overflowY="auto">
                {images.map((image) => (
                  <Box
                    key={image.id}
                    border="1px solid"
                    borderColor="gray.200"
                    borderRadius="md"
                    p={2}
                  >
                    <VStack gap={2}>
                      <Text fontSize="sm" fontWeight="medium">
                        {image.filename}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        Size: {Math.round(image.file_size / 1024)}KB
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        Uploaded: {new Date(image.date_uploaded).toLocaleDateString()}
                      </Text>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewImage(image.id)}
                        loading={imageLoading}
                      >
                        View Image
                      </Button>
                    </VStack>
                  </Box>
                ))}
              </VStack>
            )}
          </DialogBody>
          <DialogCloseTrigger />
        </DialogContent>
      </DialogRoot>

      {/* Image viewer modal */}
      {selectedImage && (
        <DialogRoot
          size="xl"
          placement="center"
          open={!!selectedImage}
          onOpenChange={({ open }) => {
            if (!open) closeImage()
          }}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Image Viewer</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Box textAlign="center">
                <img
                  src={selectedImage}
                  alt="Feedback image"
                  style={{
                    maxWidth: "100%",
                    maxHeight: "70vh",
                    objectFit: "contain",
                  }}
                />
              </Box>
            </DialogBody>
            <DialogCloseTrigger />
          </DialogContent>
        </DialogRoot>
      )}
    </>
  )
}

// feedback submission component
function AddFeedback() {
  const [isOpen, setIsOpen] = useState(false)
  const [images, setImages] = useState<File[]>([])
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<FeedbackFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      description: "",
      feedback_type: "general_feedback" as FeedbackType,
    },
  })

  const onSubmit: SubmitHandler<FeedbackFormData> = async (data) => {
    try {
      await FeedbackService.createFeedback({
        formData: {
          title: data.title,
          description: data.description,
          feedback_type: data.feedback_type,
          images: images.length > 0 ? images : undefined,
        },
      })

      showSuccessToast("Feedback submitted successfully!")
      reset()
      setImages([])
      setIsOpen(false)

      // invalidate feedback query to refresh the list
      queryClient.invalidateQueries({ queryKey: ["feedback"] })
    } catch (error) {
      console.error("Error submitting feedback:", error)
      showErrorToast("Failed to submit feedback. Please try again.")
    }
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-feedback" my={4}>
          <FiPlus fontSize="16px" />
          Submit Feedback
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Submit Feedback</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>
              Help us improve by sharing your feedback, suggestions, or reporting issues.
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
                    minLength: {
                      value: 1,
                      message: "Title must be at least 1 character.",
                    },
                    maxLength: {
                      value: 255,
                      message: "Title must be less than 255 characters.",
                    },
                  })}
                  placeholder="Brief title for your feedback"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.feedback_type}
                errorText={errors.feedback_type?.message}
                label="Feedback Type"
              >
                <select
                  id="feedback_type"
                  {...register("feedback_type", {
                    required: "Feedback type is required.",
                  })}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #e2e8f0",
                    borderRadius: "6px",
                    fontSize: "14px",
                  }}
                >
                  <option value="feature_request">Feature Request</option>
                  <option value="bug_report">Bug Report</option>
                  <option value="general_feedback">General Feedback</option>
                  <option value="improvement_suggestion">Improvement Suggestion</option>
                  <option value="other">Other</option>
                </select>
              </Field>

              <Field
                required
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Textarea
                  id="description"
                  {...register("description", {
                    required: "Description is required.",
                    minLength: {
                      value: 1,
                      message: "Description must be at least 1 character.",
                    },
                    maxLength: {
                      value: 2000,
                      message: "Description must be less than 2000 characters.",
                    },
                  })}
                  placeholder="Please provide detailed description of your feedback, suggestion, or issue..."
                  rows={4}
                />
              </Field>

              <Field label="Images (Optional)">
                <ImageUpload images={images} onImagesChange={setImages} />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button variant="subtle" colorPalette="gray" disabled={isSubmitting}>
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button variant="solid" type="submit" disabled={!isValid} loading={isSubmitting}>
              Submit Feedback
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

function FeedbackTable({ isAdmin = false }: { isAdmin?: boolean }) {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getFeedbackQueryOptions({ page, isAdmin }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const items = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return (
      <VStack gap={4} py={8}>
        <Text>Loading feedback...</Text>
      </VStack>
    )
  }

  if (items.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiMessageSquare />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>
              {isAdmin ? "No feedback submissions found" : "You haven't submitted any feedback yet"}
            </EmptyState.Title>
            <EmptyState.Description>
              {isAdmin
                ? "There are no feedback submissions in the system"
                : "Share your thoughts, suggestions, or report issues to help us improve"}
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Type</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Status</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Date Submitted</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Last Updated</Table.ColumnHeader>
            {isAdmin && <Table.ColumnHeader w="sm">User</Table.ColumnHeader>}
            <Table.ColumnHeader w="sm">Admin Response</Table.ColumnHeader>
            {isAdmin && <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>}
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {items?.map((item) => (
            <Table.Row key={item.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                <VStack align="start" gap={1}>
                  <Text fontWeight="medium">{item.title}</Text>
                  <Text
                    fontSize="sm"
                    color="gray.600"
                    style={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                    }}
                  >
                    {item.description}
                  </Text>
                </VStack>
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                <Badge colorPalette="blue" size="sm">
                  {getFeedbackTypeLabel(item.feedback_type)}
                </Badge>
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                <Badge colorPalette={getStatusColor(item.status ?? "open")} size="sm">
                  {item.status?.replace("_", " ").toUpperCase()}
                </Badge>
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {new Date(item.date_created).toLocaleDateString()}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {new Date(item.date_modified).toLocaleDateString()}
              </Table.Cell>
              {isAdmin && (
                <Table.Cell truncate maxW="sm">
                  <Text fontSize="sm" color="gray.600" fontFamily="mono">
                    {item.user_id.substring(0, 8)}...
                  </Text>
                </Table.Cell>
              )}
              <Table.Cell truncate maxW="sm">
                {item.admin_notes ? (
                  <Text
                    fontSize="sm"
                    color="gray.600"
                    style={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                    }}
                  >
                    {item.admin_notes}
                  </Text>
                ) : (
                  <Text fontSize="sm" color="gray.400">
                    No response yet
                  </Text>
                )}
                {item.image_count && item.image_count > 0 && (
                  <Box mt={2}>
                    {isAdmin ? (
                      <FeedbackImagesViewer feedbackId={item.id} imageCount={item.image_count} />
                    ) : (
                      <Text fontSize="xs" color="blue.600">
                        <FiImage size={12} style={{ display: "inline", marginRight: "4px" }} />
                        {item.image_count} image{item.image_count !== 1 ? "s" : ""} attached
                      </Text>
                    )}
                  </Box>
                )}
              </Table.Cell>
              {isAdmin && (
                <Table.Cell truncate maxW="sm">
                  <AdminFeedbackUpdate
                    feedbackId={item.id}
                    currentStatus={item.status}
                    currentNotes={item.admin_notes}
                  />
                </Table.Cell>
              )}
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

export const Route = createFileRoute("/_layout/feedback")({
  component: Feedback,
  validateSearch: (search) => feedbackSearchSchema.parse(search),
})

function Feedback() {
  const { user } = useAuth()
  const isAdmin = user?.is_superuser || false

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box>
          <HStack justify="space-between" align="center" mb={4}>
            <Heading size="lg">
              {isAdmin ? "Feedback Management (Admin)" : "Feedback Management"}
            </Heading>
            {isAdmin && (
              <HStack gap={2}>
                <FiShield size={20} color="orange" />
                <Text fontSize="sm" color="orange.600" fontWeight="medium">
                  Admin Mode
                </Text>
              </HStack>
            )}
          </HStack>
          {!isAdmin && <AddFeedback />}
        </Box>
        <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={4} bg="bg">
          <FeedbackTable isAdmin={isAdmin} />
        </Box>
      </VStack>
    </Container>
  )
}
