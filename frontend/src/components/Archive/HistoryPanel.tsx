import { Box, Card, Heading, Text, VStack, HStack, Spinner } from "@chakra-ui/react"
import { Switch } from "@chakra-ui/react"
import { Tooltip } from "@/components/ui/tooltip"
import { format } from "date-fns"
import { FiFileText, FiDatabase, FiUsers, FiThumbsUp, FiThumbsDown } from "react-icons/fi"

interface HistoryPanelProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  emptyMessage?: string
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
}

const HistoryPanel = ({
  reportHistory,
  selectedHistoryReport,
  isHistoryLoading,
  onLoadReport,
  emptyMessage = "No previous items",
  showAllUsers = false,
  onToggleShowAllUsers,
}: HistoryPanelProps) => {
  const getDisplayTitle = (item: any) => {
    // Try different possible title fields
    return (
      item?.document_name ||
      item?.title ||
      item?.name ||
      item?.comparison_name ||
      item?.form_name ||
      "Unnamed item"
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
    return null
  }

  const getMetadata = (item: any) => {
    // Show relevant metadata for each tool type
    if (item?.qa_count > 0) {
      return `${item.qa_count} question${item.qa_count !== 1 ? "s" : ""}`
    }
    if (item?.topic_count > 0) {
      return `${item.topic_count} topic${item.topic_count !== 1 ? "s" : ""}`
    }
    if (item?.field_count > 0) {
      return `${item.field_count} field${item.field_count !== 1 ? "s" : ""}`
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
            reportHistory.map((item: any) => (
              <Box
                key={item?.id}
                p={3}
                borderWidth="1px"
                borderRadius="md"
                cursor="pointer"
                bg={selectedHistoryReport?.id === item?.id ? "accent.subtle" : "surface"}
                _hover={{ bg: "accent.subtle" }}
                onClick={() => item?.id && onLoadReport(item.id)}
                flexShrink={0}
              >
                <VStack align="start" gap={1} width="100%">
                  <HStack gap={1} width="100%" justify="space-between">
                    <Text fontSize="xs" color="gray.500">
                      {item?.date_created
                        ? format(new Date(item.date_created as string), "dd/MM/yyyy HH:mm")
                        : "Unknown date"}
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
