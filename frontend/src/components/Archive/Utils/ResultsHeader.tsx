import React from "react"
import { Heading, HStack, Button } from "@chakra-ui/react"
import { FiCopy, FiCheck, FiDownload } from "react-icons/fi"

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
        <Button
          size="sm"
          variant="outline"
          onClick={onDownloadReport}
          loading={loadingDownload}
          colorPalette="green"
        >
          <FiDownload />
          Download DOCX
        </Button>
      </HStack>
    </HStack>
  )
}

export default ResultsHeader
