import { Tooltip } from "@/components/ui/tooltip"
import HelpTooltip from "@/components/ui/help-tooltip"
import { Box, Card, HStack, Heading, IconButton, Spinner, Text, VStack } from "@chakra-ui/react"
import { Switch } from "@chakra-ui/react"
import { format } from "date-fns"
import { useTranslation } from "react-i18next"
import { FiDatabase, FiFileText, FiThumbsDown, FiThumbsUp, FiTrash2, FiUsers } from "react-icons/fi"

interface HistoryPanelProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  onDeleteReport?: (reportId: string) => void
  emptyMessage?: string
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
}

const HistoryPanel = ({
  reportHistory,
  selectedHistoryReport,
  isHistoryLoading,
  onLoadReport,
  onDeleteReport,
  emptyMessage = "No previous items",
  showAllUsers = false,
  onToggleShowAllUsers,
}: HistoryPanelProps) => {
  const { t } = useTranslation()

  const getDisplayTitle = (item: any) => {
    // Try different possible title fields
    return (
      item?.document_name ||
      item?.title ||
      item?.name ||
      item?.comparison_name ||
      item?.form_name ||
      t("archive.unnamedItem")
    )
  }

  const getSubtitle = (item: any) => {
    // For different tools, show different subtitle information
    if (item?.kb_name) {
      return item.kb_name
    }
    if (item?.document1_name && item?.document2_name) {
      return `${item.document1_name} vs ${item.document2_name}`
    }
    if (item?.form_type) {
      return item.form_type
    }

    // Enhanced FormConnect display with actual filenames
    if (item?.digitized_files?.length > 0 || item?.handwritten_files?.length > 0) {
      const digitized = item.digitized_files || []
      const handwritten = item.handwritten_files || []
      const allFiles = [...digitized, ...handwritten]

      if (allFiles.length === 1) {
        return allFiles[0]
      }
      if (allFiles.length === 2) {
        return `${allFiles[0]} vs ${allFiles[1]}`
      }
      if (allFiles.length <= 4) {
        return allFiles.join(", ")
      }
      return `${allFiles[0]}, ${allFiles[1]}, +${allFiles.length - 2} more`
    }

    // Fallback to the existing logic for FormConnect (for backward compatibility)
    if (
      item?.metadata?.digitized_files?.length > 0 ||
      item?.metadata?.handwritten_files?.length > 0
    ) {
      const digitizedCount = item.metadata.digitized_files?.length || 0
      const handwrittenCount = item.metadata.handwritten_files?.length || 0
      const parts = []
      if (digitizedCount > 0) parts.push(`${digitizedCount} ${t("archive.metadata.digitized")}`)
      if (handwrittenCount > 0)
        parts.push(`${handwrittenCount} ${t("archive.metadata.handwritten")}`)
      return parts.join(", ")
    }

    return null
  }

  const getMetadata = (item: any) => {
    // Show relevant metadata for each tool type
    if (item?.qa_count > 0) {
      return item.qa_count === 1
        ? `1 ${t("archive.metadata.question")}`
        : `${item.qa_count} ${t("archive.metadata.questions")}`
    }
    if (item?.topic_count > 0) {
      return item.topic_count === 1
        ? `1 ${t("archive.metadata.topic")}`
        : `${item.topic_count} ${t("archive.metadata.topics")}`
    }
    if (item?.field_count > 0) {
      const fieldText =
        item.field_count === 1
          ? `1 ${t("archive.metadata.field")}`
          : `${item.field_count} ${t("archive.metadata.fields")}`
      // For FormConnect, also show document count if available
      if (item?.document_count > 0) {
        const docText =
          item.document_count === 1
            ? `1 ${t("archive.metadata.document")}`
            : `${item.document_count} ${t("archive.metadata.documents")}`
        return `${fieldText}, ${docText}`
      }
      return fieldText
    }
    return null
  }

  return (
    <Card.Root height="fit-content">
      <Card.Header pb={2}>
        <HStack justifyContent="space-between" width="100%">
          <Heading size="md">{t("archive.history")}</Heading>
          {onToggleShowAllUsers && (
            <Tooltip
              content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
            >
              <HStack gap={2}>
                <HStack gap={1} align="center">
                  <Text fontSize="xs" color="gray.500">
                    {t("archive.allUsers")}
                  </Text>
                  <HelpTooltip helpKey="allUsersToggle" />
                </HStack>
                {/* Key added to force remounting when showAllUsers changes */}
                <Switch.Root
                  key={`switch-${showAllUsers}`}
                  size="sm"
                  colorPalette="blue"
                  checked={showAllUsers}
                >
                  <Switch.HiddenInput
                    checked={showAllUsers}
                    onChange={() => {
                      console.log(
                        "HistoryPanel toggle clicked, current showAllUsers:",
                        showAllUsers,
                      )
                      if (onToggleShowAllUsers) onToggleShowAllUsers()
                    }}
                  />
                  <Switch.Control data-state={showAllUsers ? "checked" : "unchecked"}>
                    <Switch.Thumb />
                  </Switch.Control>
                </Switch.Root>
              </HStack>
            </Tooltip>
          )}
        </HStack>
      </Card.Header>
      <Card.Body p={2}>
        <VStack align="stretch" gap={2} height="540px" overflowY="auto">
          {isHistoryLoading ? (
            <Spinner size="sm" alignSelf="center" justifySelf="center" />
          ) : !reportHistory || reportHistory.length === 0 ? (
            <Text fontSize="sm" color="gray.500">
              {emptyMessage}
            </Text>
          ) : (
            reportHistory.map((item: any) => (
              <Box
                key={item?.id}
                p={3}
                borderWidth="2px"
                borderRadius="md"
                cursor="pointer"
                bg={selectedHistoryReport?.id === item?.id ? "blue.50" : "surface"}
                borderColor={selectedHistoryReport?.id === item?.id ? "blue.300" : "border"}
                _hover={{
                  bg: selectedHistoryReport?.id === item?.id ? "blue.100" : "accent.subtle",
                  borderColor: selectedHistoryReport?.id === item?.id ? "blue.400" : "border",
                }}
                onClick={() => item?.id && onLoadReport(item.id)}
                flexShrink={0}
                position="relative"
                transition="all 0.2s"
                shadow={selectedHistoryReport?.id === item?.id ? "md" : "sm"}
              >
                {/* Delete button */}
                {onDeleteReport && (
                  <Box position="absolute" top={2} right={2} zIndex={10}>
                    <IconButton
                      size="xs"
                      variant="ghost"
                      colorScheme="red"
                      aria-label="Delete"
                      onClick={(e) => {
                        e.stopPropagation()
                        // Add confirmation dialog
                        if (window.confirm(t("archive.deleteConfirmation"))) {
                          onDeleteReport(item.id)
                        }
                      }}
                    >
                      <FiTrash2 size={12} />
                    </IconButton>
                  </Box>
                )}

                <VStack align="start" gap={1} width="100%">
                  <HStack gap={1} width="100%" justify="space-between">
                    <Text fontSize="xs" color="gray.500">
                      {item?.date_created
                        ? format(new Date(item.date_created as string), "dd/MM/yyyy HH:mm")
                        : t("archive.unknownDate")}
                    </Text>
                    {getMetadata(item) && (
                      <Text fontSize="xs" color="gray.500">
                        {getMetadata(item)}
                      </Text>
                    )}
                  </HStack>

                  {/* Show user info when viewing all users */}
                  {showAllUsers && item?.user_name && (
                    <HStack gap={1} width="100%">
                      <FiUsers size={12} />
                      <Text fontSize="xs" color="gray.500">
                        {item.user_name}
                      </Text>
                    </HStack>
                  )}

                  <HStack gap={1} width="100%" justify="space-between">
                    <HStack gap={1}>
                      <FiFileText size={12} color="blue" />
                      <Text fontWeight="medium" fontSize="sm" lineClamp={1}>
                        {getDisplayTitle(item)}
                      </Text>
                    </HStack>

                    {/* Show feedback icon if feedback exists */}
                    {item?.has_feedback && (
                      <Tooltip
                        content={
                          typeof item.feedback === "object" && item.feedback?.feedback === "correct"
                            ? t("archive.feedback.positive")
                            : typeof item.feedback === "object" &&
                                item.feedback?.feedback === "incorrect"
                              ? t("archive.feedback.negative")
                              : item.feedback === "correct" || item.feedback === "positive"
                                ? t("archive.feedback.positive")
                                : item.feedback === "incorrect" || item.feedback === "negative"
                                  ? t("archive.feedback.negative")
                                  : t("archive.feedback.hasFeedback")
                        }
                      >
                        {typeof item.feedback === "object" &&
                        item.feedback?.feedback === "correct" ? (
                          <FiThumbsUp size={14} color="green" />
                        ) : typeof item.feedback === "object" &&
                          item.feedback?.feedback === "incorrect" ? (
                          <FiThumbsDown size={14} color="red" />
                        ) : item.feedback === "correct" || item.feedback === "positive" ? (
                          <FiThumbsUp size={14} color="green" />
                        ) : item.feedback === "incorrect" || item.feedback === "negative" ? (
                          <FiThumbsDown size={14} color="red" />
                        ) : (
                          <FiThumbsUp size={14} color="green" opacity={0.7} />
                        )}
                      </Tooltip>
                    )}
                  </HStack>

                  {getSubtitle(item) && (
                    <HStack gap={1} width="100%">
                      <FiDatabase size={12} color="gray" />
                      {/* Add tooltip for FormConnect files when there are many */}
                      {item?.digitized_files?.length > 0 || item?.handwritten_files?.length > 0 ? (
                        <Tooltip
                          content={
                            [...(item.digitized_files || []), ...(item.handwritten_files || [])]
                              .length > 4
                              ? [
                                  ...(item.digitized_files || []),
                                  ...(item.handwritten_files || []),
                                ].join(", ")
                              : undefined
                          }
                        >
                          <Text fontSize="xs" color="gray.600" lineClamp={1}>
                            {getSubtitle(item)}
                          </Text>
                        </Tooltip>
                      ) : (
                        <Text fontSize="xs" color="gray.600" lineClamp={1}>
                          {getSubtitle(item)}
                        </Text>
                      )}
                    </HStack>
                  )}
                </VStack>
              </Box>
            ))
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default HistoryPanel
