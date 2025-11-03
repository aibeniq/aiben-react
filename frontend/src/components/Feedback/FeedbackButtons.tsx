import { FeedbackService } from "@/client"
import { Tooltip } from "@/components/ui/tooltip"
import useCustomToast from "@/hooks/useCustomToast"
import {
  Box,
  Button,
  HStack,
  IconButton,
  Portal,
  Text,
  Textarea,
} from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import { FiThumbsDown, FiThumbsUp } from "react-icons/fi"

interface FeedbackButtonsProps {
  interactionId: string
  onFeedbackSubmitted?: (type: string) => void
  existingFeedback?: {
    feedback: "correct" | "incorrect" | null
    feedbackText?: string
    feedbackDate?: string
  }
}

const FeedbackButtons = ({
  interactionId,
  onFeedbackSubmitted,
  existingFeedback,
}: FeedbackButtonsProps) => {
  const { t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [feedbackType, setFeedbackType] = useState<
    "correct" | "incorrect" | null
  >(existingFeedback?.feedback || null)
  const [feedbackText, setFeedbackText] = useState(
    existingFeedback?.feedbackText || "",
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Helper function for safer translation retrieval
  const getTranslation = (key: string, fallback: string) => {
    try {
      // Try to get the translation
      const translated = t(key)

      // If the translation doesn't exist or is the same as the key, use fallback
      if (
        !translated ||
        translated === key ||
        translated.startsWith("[missing key]")
      ) {
        return fallback
      }
      return translated
    } catch (error) {
      console.error(`Translation error for "${key}":`, error)
      return fallback
    }
  }

  // Effect to update state when existingFeedback changes
  useEffect(() => {
    if (existingFeedback) {
      setFeedbackType(existingFeedback.feedback)
      setFeedbackText(existingFeedback.feedbackText || "")
    }
  }, [existingFeedback])

  // Open the modal and set the feedback type
  const handleFeedbackClick = (type: "correct" | "incorrect") => {
    // If this type is already selected and there's existing feedback,
    // we're editing the current feedback
    const isEditing = existingFeedback?.feedback === type

    setFeedbackType(type)

    // If editing, keep the existing text, otherwise clear it
    if (!isEditing) {
      setFeedbackText("")
    }

    setIsModalOpen(true)
  }

  // Focus the textarea when modal opens
  useEffect(() => {
    if (isModalOpen && textareaRef.current) {
      setTimeout(() => {
        textareaRef.current?.focus()
      }, 100)
    }
  }, [isModalOpen])

  // Close the modal
  const handleClose = () => {
    setIsModalOpen(false)
  }

  // Submit feedback
  const handleSubmitFeedback = async () => {
    if (!feedbackType) return

    setIsSubmitting(true)
    try {
      await FeedbackService.submitFeedback({
        interactionId: interactionId,
        feedback: feedbackType,
        feedbackText: feedbackText.trim() || undefined,
      })

      showSuccessToast(
        getTranslation(
          "feedback.thankYouMessage",
          "Thank you for your feedback!",
        ),
      )
      setIsModalOpen(false)
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(feedbackType)
      }
    } catch (error) {
      console.error("Failed to submit feedback:", error)
      showErrorToast(
        getTranslation(
          "feedback.submitErrorMessage",
          "Failed to submit feedback. Please try again.",
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Box position="relative" zIndex={10}>
      {/* Feedback buttons */}
      <HStack
        gap={2}
        bg="bg"
        p={1}
        borderRadius="md"
        boxShadow="sm"
        border="1px solid"
        borderColor="gray.200"
      >
        <Tooltip
          content={
            existingFeedback?.feedback === "correct"
              ? getTranslation(
                  "feedback.tooltipEditPositive",
                  "Edit your helpful feedback",
                )
              : getTranslation(
                  "feedback.tooltipMarkPositive",
                  "Mark as helpful",
                )
          }
          showArrow
        >
          <IconButton
            aria-label="Mark as helpful"
            size="sm"
            variant={feedbackType === "correct" ? "solid" : "ghost"}
            colorPalette="green"
            onClick={() => handleFeedbackClick("correct")}
          >
            <FiThumbsUp
              size={18}
              color={feedbackType === "correct" ? "white" : "green"}
            />
          </IconButton>
        </Tooltip>

        <Tooltip
          content={
            existingFeedback?.feedback === "incorrect"
              ? getTranslation(
                  "feedback.tooltipEditNegative",
                  "Edit your feedback for improvements",
                )
              : getTranslation(
                  "feedback.tooltipMarkNegative",
                  "Mark as not helpful",
                )
          }
          showArrow
        >
          <IconButton
            aria-label="Mark as unhelpful"
            size="sm"
            variant={feedbackType === "incorrect" ? "solid" : "ghost"}
            colorPalette="red"
            onClick={() => handleFeedbackClick("incorrect")}
          >
            <FiThumbsDown
              size={18}
              color={feedbackType === "incorrect" ? "white" : "red"}
            />
          </IconButton>
        </Tooltip>

        {existingFeedback?.feedbackDate && (
          <Tooltip
            content={`Feedback submitted on ${new Date(existingFeedback.feedbackDate).toLocaleDateString()} at ${new Date(existingFeedback.feedbackDate).toLocaleTimeString()}`}
            showArrow
          >
            <Text fontSize="xs" color="gray.500" ml={1}>
              {getTranslation("feedback.feedbackSaved", "Feedback saved")}
            </Text>
          </Tooltip>
        )}
      </HStack>

      {/* Feedback modal using Portal */}
      {isModalOpen && (
        <Portal>
          <Box
            position="fixed"
            top="0"
            left="0"
            right="0"
            bottom="0"
            bg="rgba(0,0,0,0.5)"
            zIndex={1000}
            display="flex"
            alignItems="center"
            justifyContent="center"
            onClick={handleClose}
          >
            <Box
              bg="bg"
              borderRadius="md"
              maxWidth="90vw"
              width="400px"
              boxShadow="lg"
              onClick={(e) => e.stopPropagation()}
              p={4}
            >
              <Text fontWeight="semibold" fontSize="lg" mb={3}>
                {feedbackType === "correct"
                  ? getTranslation(
                      "feedback.modalTitlePositive",
                      "What was helpful?",
                    )
                  : getTranslation(
                      "feedback.modalTitleNegative",
                      "What could be improved?",
                    )}
              </Text>

              <Text fontSize="sm" mb={2}>
                {feedbackType === "correct"
                  ? getTranslation(
                      "feedback.descriptionPositive",
                      "Tell us what you liked about this response.",
                    )
                  : getTranslation(
                      "feedback.descriptionNegative",
                      "Tell us how we can improve this response.",
                    )}
              </Text>

              <Textarea
                ref={textareaRef}
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder={getTranslation(
                  "feedback.placeholder",
                  "Your comments (optional)",
                )}
                size="md"
                resize="vertical"
                rows={4}
                mb={4}
              />

              <HStack justifyContent="flex-end" gap={3}>
                <Button size="sm" variant="outline" onClick={handleClose}>
                  {getTranslation("feedback.cancel", "Cancel")}
                </Button>
                <Button
                  size="sm"
                  colorPalette={feedbackType === "correct" ? "green" : "red"}
                  onClick={handleSubmitFeedback}
                  loading={isSubmitting}
                >
                  {existingFeedback?.feedback
                    ? getTranslation(
                        "feedback.updateFeedback",
                        "Update Feedback",
                      )
                    : getTranslation("feedback.submit", "Submit")}
                </Button>
              </HStack>
            </Box>
          </Box>
        </Portal>
      )}
    </Box>
  )
}

export default FeedbackButtons
