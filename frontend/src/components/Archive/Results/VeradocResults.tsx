import React from "react"
import { Box } from "@chakra-ui/react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import QAPairDisplay from "../Utils/QAPairDisplay"
import { VeradocGetVeradocDetailResponse } from "../../../client"

interface VeradocResultsProps {
  selectedReport: VeradocGetVeradocDetailResponse
  components: any // Markdown components for table rendering
}

const VeradocResults: React.FC<VeradocResultsProps> = ({ selectedReport, components }) => {
  const results = selectedReport.results.final_evaluation || ""
  const qaPairs = selectedReport.results.qa_pairs || []

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}

      {/* Show Q&A pairs for Veradoc */}
      {qaPairs.length > 0 && (
        <Box mt={4}>
          {qaPairs.map((pair: any, index: number) => (
            <QAPairDisplay key={index} pair={pair} index={index} />
          ))}
        </Box>
      )}
    </>
  )
}

export default VeradocResults
