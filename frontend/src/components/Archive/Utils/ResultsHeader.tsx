import { Button, HStack, Heading } from "@chakra-ui/react"
import type React from "react"
import { FiCheck, FiCopy } from "react-icons/fi"
import DownloadButton from "../../ui/download-button"

interface ResultsHeaderProps {
  copySuccess: boolean
  loadingDownload: boolean
  loadingCsvDownload?: boolean
  onCopyReport: () => void
  onDownloadReport: () => void
  onDownloadCsv?: () => void
  showCsvDownload?: boolean
}

const ResultsHeader: React.FC<ResultsHeaderProps> = ({
  copySuccess,
  loadingDownload,
  loadingCsvDownload,
  onCopyReport,
  onDownloadReport,
  onDownloadCsv,
  showCsvDownload,
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
        <DownloadButton
          size="sm"
          onClick={onDownloadReport}
          loading={loadingDownload}
        >
          Download DOCX
        </DownloadButton>
        {showCsvDownload && onDownloadCsv && (
          <DownloadButton
            size="sm"
            onClick={onDownloadCsv}
            loading={loadingCsvDownload}
          >
            Download CSV
          </DownloadButton>
        )}
      </HStack>
    </HStack>
  )
}

export default ResultsHeader
