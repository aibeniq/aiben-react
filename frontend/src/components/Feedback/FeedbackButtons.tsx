import { useState, useRef, useEffect } from "react";
import {
  Box,
  HStack,
  Button,
  Textarea,
  Text,
  Portal,
  IconButton,
  useToast
} from "@chakra-ui/react";
import { Tooltip } from "@/components/ui/tooltip";
import { FiThumbsUp, FiThumbsDown, FiSend } from "react-icons/fi";
import { FeedbackService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";

interface FeedbackButtonsProps {
  interactionId: string;
  onFeedbackSubmitted?: (type: string) => void;
  existingFeedback?: {
    feedback: "correct" | "incorrect" | null;
    feedbackText?: string;
    feedbackDate?: string;
  };
}

const FeedbackButtons = ({ interactionId, onFeedbackSubmitted, existingFeedback }: FeedbackButtonsProps) => {
  // Replace useDisclosure with a simple useState
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [feedbackType, setFeedbackType] = useState<"correct" | "incorrect" | null>(
    existingFeedback?.feedback || null
  );
  const [feedbackText, setFeedbackText] = useState(existingFeedback?.feedbackText || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Effect to update state when existingFeedback changes
  useEffect(() => {
    if (existingFeedback) {
      setFeedbackType(existingFeedback.feedback);
      setFeedbackText(existingFeedback.feedbackText || "");
    }
  }, [existingFeedback]);

  // Open the modal and set the feedback type
  const handleFeedbackClick = (type: "correct" | "incorrect") => {
    console.log("Feedback button clicked:", type);
    
    // If this type is already selected and there's existing feedback,
    // we're editing the current feedback
    const isEditing = existingFeedback?.feedback === type;
    
    setFeedbackType(type);
    
    // If editing, keep the existing text, otherwise clear it
    if (!isEditing) {
      setFeedbackText("");
    }
    
    setIsModalOpen(true);
    console.log("Modal should open now for type:", type);
  };

  // Focus the textarea when modal opens
  useEffect(() => {
    if (isModalOpen && textareaRef.current) {
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  }, [isModalOpen]);

  // Close the modal
  const handleClose = () => {
    setIsModalOpen(false);
  };

  // Submit feedback
  const handleSubmitFeedback = async () => {
    console.log("Submitting feedback:", feedbackType, feedbackText);
    
    if (!feedbackType) return;
    
    setIsSubmitting(true);
    try {
      await FeedbackService.submitFeedback({
        interactionId: interactionId,
        feedback: feedbackType,
        feedbackText: feedbackText.trim() || undefined,
      });
      
      showSuccessToast("Thank you for your feedback!");
      setIsModalOpen(false);
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(feedbackType);
      }
    } catch (error) {
      console.error("Failed to submit feedback:", error);
      showErrorToast("Failed to submit feedback. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box position="relative" zIndex={10}>
      {/* Feedback buttons */}
      <HStack 
        spacing={2}
        bg="white" 
        p={1} 
        borderRadius="md" 
        boxShadow="sm"
        border="1px solid"
        borderColor="gray.200"
      >
        <Tooltip 
          label={existingFeedback?.feedback === "correct" ? "Edit your helpful feedback" : "Mark as helpful"}
          hasArrow
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
          label={existingFeedback?.feedback === "incorrect" ? "Edit your feedback for improvements" : "Mark as not helpful"}
          hasArrow
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
            label={`Feedback submitted on ${new Date(existingFeedback.feedbackDate).toLocaleDateString()} at ${new Date(existingFeedback.feedbackDate).toLocaleTimeString()}`}
            hasArrow
          >
            <Text fontSize="xs" color="gray.500" ml={1}>
              Feedback saved
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
              bg="white"
              borderRadius="md"
              maxWidth="90vw"
              width="400px"
              boxShadow="lg"
              onClick={(e) => e.stopPropagation()}
              p={4}
            >
              <Text fontWeight="semibold" fontSize="lg" mb={3}>
                {feedbackType === "correct" ? "What was helpful?" : "What could be improved?"}
              </Text>
              
              <Text fontSize="sm" mb={2}>
                {feedbackType === "correct"
                  ? "Tell us what you liked about this response."
                  : "Tell us how we can improve this response."}
              </Text>
              
              <Textarea
                ref={textareaRef}
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="Your comments (optional)"
                size="md"
                resize="vertical"
                rows={4}
                mb={4}
              />
              
              <HStack justifyContent="flex-end" spacing={3}>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleClose}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  colorPalette={feedbackType === "correct" ? "green" : "red"}
                  onClick={handleSubmitFeedback}
                  isLoading={isSubmitting}
                  leftIcon={<FiSend />}
                >
                  {existingFeedback?.feedback ? "Update Feedback" : "Submit"}
                </Button>
              </HStack>
            </Box>
          </Box>
        </Portal>
      )}
    </Box>
  );
};

export default FeedbackButtons;