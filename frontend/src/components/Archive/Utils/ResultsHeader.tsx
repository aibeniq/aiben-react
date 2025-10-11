import { Button, HStack, Heading } from "@chakra-ui/react"
import type React from "react"
import { FiCheck, FiCopy } from "react-icons/fi"
import { useTranslation } from "react-i18next"
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
  const { t } = useTranslation()
  
  return (
    <HStack justify="space-between" align="center" width="100%">
      <Heading size="md">{t("ui.results")}</Heading>
      <HStack gap={2} justifyContent="flex-end">
        <Button
          size="sm"
          variant="outline"
          onClick={onCopyReport}
          colorPalette={copySuccess ? "green" : "blue"}
        >
          {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
          {copySuccess ? t("ui.copied") : t("ui.copyText")}
        </Button>
        <DownloadButton
          size="sm"
          onClick={onDownloadReport}
          loading={loadingDownload}
        >
          {t("ui.downloadDocx")}
        </DownloadButton>
        {showCsvDownload && onDownloadCsv && (
          <DownloadButton
            size="sm"
            onClick={onDownloadCsv}
            loading={loadingCsvDownload}
          >
            {t("ui.downloadCsv")}
          </DownloadButton>
        )}
      </HStack>
    </HStack>
  )
}

export default ResultsHeader
