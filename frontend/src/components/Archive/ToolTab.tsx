import { Box, HStack } from "@chakra-ui/react"
import type React from "react"
import type { ReactNode } from "react"
import HistoryPanel from "./HistoryPanel"

interface ToolTabProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  onDeleteReport?: (reportId: string) => void
  emptyMessage: string
  children: ReactNode
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
}

const ToolTab: React.FC<ToolTabProps> = ({
  reportHistory,
  selectedHistoryReport,
  isHistoryLoading,
  onLoadReport,
  onDeleteReport,
  emptyMessage,
  children,
  showAllUsers,
  onToggleShowAllUsers,
}) => {
  // Log when the component renders with showAllUsers prop
  console.log(`ToolTab rendering with showAllUsers: ${showAllUsers}`)

  return (
    <HStack gap={4} align="stretch" height="fit-content">
      <Box minW="300px" maxW="400px" w="300px" flexShrink={0}>
        <HistoryPanel
          reportHistory={reportHistory}
          selectedHistoryReport={selectedHistoryReport}
          isHistoryLoading={isHistoryLoading}
          onLoadReport={onLoadReport}
          onDeleteReport={onDeleteReport}
          emptyMessage={emptyMessage}
          showAllUsers={showAllUsers}
          onToggleShowAllUsers={onToggleShowAllUsers}
        />
      </Box>
      <Box flex={1}>{children}</Box>
    </HStack>
  )
}

export default ToolTab
