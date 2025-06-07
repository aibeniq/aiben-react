import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface FormconnectResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const FormconnectResults: React.FC<FormconnectResultsProps> = ({ selectedReport, components }) => {
  const results = selectedReport.results?.comparison || selectedReport.results?.message || ""

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

export default FormconnectResults
