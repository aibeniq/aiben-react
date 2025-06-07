import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface ReportgenieResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const ReportgenieResults: React.FC<ReportgenieResultsProps> = ({ selectedReport, components }) => {
  const results =
    selectedReport.results?.full_report ||
    selectedReport.full_report ||
    selectedReport.content ||
    ""

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}
    </>
  )
}

export default ReportgenieResults
