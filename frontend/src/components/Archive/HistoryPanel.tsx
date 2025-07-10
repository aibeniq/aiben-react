import { Box, Card, Heading, Text, VStack, HStack, Spinner } from "@chakra-ui/react"
import { Switch } from "@chakra-ui/react"
import { Tooltip } from "@/components/ui/tooltip"
import { format } from "date-fns"
import { FiFileText, FiDatabase, FiUsers, FiThumbsUp, FiThumbsDown } from "react-icons/fi"
import { ReportGenieHistoryItem, VeraDocHistoryItem } from "@/client"

// Base interface for history items - common fields across all tools
interface BaseHistoryItem {
  id: string
  date_created: string
  has_feedback?: boolean
  feedback?: any
  user_name?: string | null
}

// Union type for all possible history item types
type HistoryItem =
  | ReportGenieHistoryItem
  | VeraDocHistoryItem
  | (BaseHistoryItem & { [key: string]: unknown })

interface HistoryPanelProps<T extends HistoryItem = HistoryItem> {
  reportHistory: T[]
  selectedHistoryReport: T | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  emptyMessage?: string
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
}

const HistoryPanel = <T extends HistoryItem = HistoryItem>({
  reportHistory,
  selectedHistoryReport,
  isHistoryLoading,
  onLoadReport,
  emptyMessage = "No previous items",
  showAllUsers = false,
  onToggleShowAllUsers,
}: HistoryPanelProps<T>) => {
  const getDisplayTitle = (item: T): string => {
    // ReportGenie has a typed 'title' field
    if ("title" in item && typeof item.title === "string" && item.title) {
      return item.title
    }

    // Try different possible title fields for other tools
    const anyItem = item as any
    return (
      anyItem?.document_name ||
      anyItem?.name ||
      anyItem?.comparison_name ||
      anyItem?.form_name ||
      "Unnamed item"
    )
  }

  const getSubtitle = (item: T): string | null => {
    // ReportGenie has a typed 'kb_name' field
    if ("kb_name" in item && typeof item.kb_name === "string" && item.kb_name) {
      return item.kb_name
    }

    // For other tools, check untyped fields
    const anyItem = item as any
    if (anyItem?.document1_name && anyItem?.document2_name) {
      return `${anyItem.document1_name} vs ${anyItem.document2_name}`
    }
    if (anyItem?.form_type) {
      return anyItem.form_type
    }
    return null
  }

  const getMetadata = (item: T): string | null => {
    // ReportGenie has a typed 'section_count' field
    if (
      "section_count" in item &&
      typeof item.section_count === "number" &&
      item.section_count > 0
    ) {
      return `${item.section_count} section${item.section_count !== 1 ? "s" : ""}`
    }

    // For other tools, check untyped fields
    const anyItem = item as any
    if (anyItem?.qa_count > 0) {
      return `${anyItem.qa_count} question${anyItem.qa_count !== 1 ? "s" : ""}`
    }
    if (anyItem?.topic_count > 0) {
      return `${anyItem.topic_count} topic${anyItem.topic_count !== 1 ? "s" : ""}`
    }
    if (anyItem?.field_count > 0) {
      return `${anyItem.field_count} field${anyItem.field_count !== 1 ? "s" : ""}`
    }
    return null
  }

  return (
    <Card.Root height="fit-content">
      <Card.Header pb={2}>
        <HStack justifyContent="space-between" width="100%">
          <Heading size="md">History</Heading>
          {onToggleShowAllUsers && (
            <Tooltip
              content={showAllUsers ? "Viewing all users' history" : "Viewing only my history"}
            >
              <HStack gap={2}>
                <Text fontSize="xs" color="gray.500">
                  All Users
                </Text>
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
            reportHistory.map((item: T) => (
              <Box
                key={item.id}
                p={3}
                borderWidth="1px"
                borderRadius="md"
                cursor="pointer"
                bg={selectedHistoryReport?.id === item.id ? "accent.subtle" : "surface"}
                _hover={{ bg: "accent.subtle" }}
                onClick={() => onLoadReport(item.id)}
                flexShrink={0}
              >
                <VStack align="start" gap={1} width="100%">
                  <HStack gap={1} width="100%" justify="space-between">
                    <Text fontSize="xs" color="gray.500">
                      {format(new Date(item.date_created), "dd/MM/yyyy HH:mm")}
                    </Text>
                    {getMetadata(item) && (
                      <Text fontSize="xs" color="gray.500">
                        {getMetadata(item)}
                      </Text>
                    )}
                  </HStack>

                  {/* Show user info when viewing all users */}
                  {showAllUsers && item.user_name && (
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
                    {item.has_feedback && (
                      <Tooltip
                        content={
                          typeof item.feedback === "object" && item.feedback?.feedback === "correct"
                            ? "Positive feedback"
                            : typeof item.feedback === "object" &&
                                item.feedback?.feedback === "incorrect"
                              ? "Negative feedback"
                              : item.feedback === "correct" || item.feedback === "positive"
                                ? "Positive feedback"
                                : item.feedback === "incorrect" || item.feedback === "negative"
                                  ? "Negative feedback"
                                  : "Has feedback"
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
                      <Text fontSize="xs" color="gray.600" lineClamp={1}>
                        {getSubtitle(item)}
                      </Text>
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
