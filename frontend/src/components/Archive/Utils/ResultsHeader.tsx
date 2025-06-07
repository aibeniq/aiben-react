import React from "react"
import { Heading, HStack, Button } from "@chakra-ui/react"
import { FiCopy, FiCheck } from "react-icons/fi"
import DownloadButton from "../../ui/download-button"

interface ResultsHeaderProps {
  copySuccess: boolean
  loadingDownload: boolean
  onCopyReport: () => void
  onDownloadReport: () => void
}

const ResultsHeader: React.FC<ResultsHeaderProps> = ({
  copySuccess,
  loadingDownload,
  onCopyReport,
  onDownloadReport,
}) => {
  return (
    <HStack justify="space-between" align="center" width="100%">
      <Heading size="md">Results</Heading>
      <HStack gap={2} justifyContent="flex-end">
        <Button
          size="sm"
          variant="outline"
          onClick={onCopyReport}
          colorPalette={copySuccess ? "green" : "blue"}
        >
          {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
          {copySuccess ? "Copied!" : "Copy Text"}
        </Button>
        <DownloadButton size="sm" onClick={onDownloadReport} loading={loadingDownload}>
          Download DOCX
        </DownloadButton>
      </HStack>
    </HStack>
  )
}

export default ResultsHeader
