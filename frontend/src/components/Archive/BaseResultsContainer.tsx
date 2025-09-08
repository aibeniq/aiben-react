import { Box } from "@chakra-ui/react"
import type React from "react"
import type { ReactNode } from "react"
import FeedbackButtons from "../Feedback/FeedbackButtons"
import ResultsHeader from "./Utils/ResultsHeader"

interface BaseResultsContainerProps {
  children: ReactNode
  selectedReport?: any
  copySuccess: boolean
  loadingDownload: boolean
  loadingCsvDownload?: boolean
  onCopyReport: () => void
  onDownloadReport: () => void
  onDownloadCsv?: () => void
  showCsvDownload?: boolean
  onFeedbackSubmitted: (type: string) => void
  showFeedback?: boolean
}

const BaseResultsContainer: React.FC<BaseResultsContainerProps> = ({
  children,
  selectedReport,
  copySuccess,
  loadingDownload,
  loadingCsvDownload,
  onCopyReport,
  onDownloadReport,
  onDownloadCsv,
  showCsvDownload,
  onFeedbackSubmitted,
  showFeedback = true,
}) => {
  return (
    <Box
      border="1px solid"
      borderColor="border"
      borderRadius="md"
      p={4}
      bg="surface"
      minH="100px"
      maxH="600px"
      overflowY="auto"
      position="relative"
    >
      <Box position="absolute" left={4} top={4} right={4} zIndex={20}>
        <ResultsHeader
          copySuccess={copySuccess}
          loadingDownload={loadingDownload}
          loadingCsvDownload={loadingCsvDownload}
          onCopyReport={onCopyReport}
          onDownloadReport={onDownloadReport}
          onDownloadCsv={onDownloadCsv}
          showCsvDownload={showCsvDownload}
        />
      </Box>

      <Box mt={12}>{children}</Box>

      {showFeedback && selectedReport?.id && (
        <Box
          position="sticky"
          bottom={4}
          right={4}
          display="flex"
          justifyContent="flex-end"
          pointerEvents="auto"
          zIndex={10}
        >
          <FeedbackButtons
            interactionId={selectedReport.id}
            onFeedbackSubmitted={onFeedbackSubmitted}
            existingFeedback={
              selectedReport.feedback
                ? {
                    feedback: selectedReport.feedback.feedback as
                      | "correct"
                      | "incorrect"
                      | null,
                    feedbackText:
                      selectedReport.feedback.feedbackText || undefined,
                    feedbackDate:
                      selectedReport.feedback.feedbackDate || undefined,
                  }
                : undefined
            }
          />
        </Box>
      )}
    </Box>
  )
}

export default BaseResultsContainer
