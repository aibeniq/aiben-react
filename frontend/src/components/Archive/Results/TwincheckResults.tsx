import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import TopicAnalysisDisplay from "../Utils/TopicAnalysisDisplay"

interface TwincheckResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const TwincheckResults: React.FC<TwincheckResultsProps> = ({ selectedReport, components }) => {
  const results = selectedReport.results?.summary || ""
  const topicAnalysis = selectedReport.results?.topic_analysis || []

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}

      <TopicAnalysisDisplay topicAnalysis={topicAnalysis} />
    </>
  )
}

export default TwincheckResults
