import React, { ReactNode } from "react"
import { HStack, Box } from "@chakra-ui/react"
import HistoryPanel from "./HistoryPanel"

interface ToolTabProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  emptyMessage: string
  children: ReactNode
}

const ToolTab: React.FC<ToolTabProps> = ({
  reportHistory,
  selectedHistoryReport,
  isHistoryLoading,
  onLoadReport,
  emptyMessage,
  children,
}) => {
  return (
    <HStack gap={4} align="stretch" height="fit-content">
      <Box minW="300px" maxW="400px" w="300px" flexShrink={0}>
        <HistoryPanel
          reportHistory={reportHistory}
          selectedHistoryReport={selectedHistoryReport}
          isHistoryLoading={isHistoryLoading}
          onLoadReport={onLoadReport}
          emptyMessage={emptyMessage}
        />
      </Box>
      <Box flex={1}>{children}</Box>
    </HStack>
  )
}

export default ToolTab
