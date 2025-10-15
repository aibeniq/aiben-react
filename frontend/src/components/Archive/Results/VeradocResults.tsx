import { Box, Text, VStack } from "@chakra-ui/react"
import type React from "react"
import { useTranslation } from "react-i18next"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { VeradocGetVeradocDetailResponse } from "../../../client"
import QAPairDisplay from "../Utils/QAPairDisplay"
import LazyQAPairDisplay from "./LazyQAPairDisplay"

interface VeradocResultsProps {
  selectedReport: VeradocGetVeradocDetailResponse
  components: any // Markdown components for table rendering
}

const VeradocResults: React.FC<VeradocResultsProps> = ({
  selectedReport,
  components,
}) => {
  const { t } = useTranslation()
  const results = (selectedReport.results as any)?.final_evaluation || ""
  const qaPairs = (selectedReport.results as any)?.qa_pairs || []
  const qaPairsSummary = (selectedReport.results as any)?.qa_pairs_summary || []

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}

      {/* Show Q&A pairs - use lazy loading if we have summaries, otherwise show full pairs */}
      {qaPairsSummary.length > 0 ? (
        <VStack mt={4} gap={3} align="stretch">
          <Text fontSize="lg" fontWeight="bold">
            {t("archive.labels.questionsAndAnswers")} ({qaPairsSummary.length})
          </Text>
          {qaPairsSummary.map((summary: any) => (
            <LazyQAPairDisplay
              key={summary.index}
              reportId={String(selectedReport.id)}
              qaPairSummary={summary}
            />
          ))}
        </VStack>
      ) : qaPairs.length > 0 ? (
        <Box mt={4}>
          {qaPairs.map((pair: any, index: number) => (
            <QAPairDisplay key={index} pair={pair} index={index} />
          ))}
        </Box>
      ) : null}
    </>
  )
}

export default VeradocResults
