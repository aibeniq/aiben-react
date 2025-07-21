import React, { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface ReportgenieResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const ReportgenieResults: React.FC<ReportgenieResultsProps> = ({ selectedReport, components }) => {
  const [expandedCitations, setExpandedCitations] = useState<{[key: number]: boolean}>({})

  if (!selectedReport) {
    return <div>No report data available</div>
  }

  const toggleCitations = (sectionIndex: number) => {
    setExpandedCitations(prev => ({
      ...prev,
      [sectionIndex]: !prev[sectionIndex]
    }))
  }

  // Helper function to get sections following VeraDoc pattern
  const getSections = (selectedReport: any) => {
    // Following VeraDoc pattern: get sections from results.sections (like qa_pairs)
    let sections = selectedReport?.results?.sections || []
    
    // If sections is a string (JSON), parse it
    if (typeof sections === 'string') {
      try {
        sections = JSON.parse(sections)
      } catch (e) {
        sections = []
      }
    }
    
    return Array.isArray(sections) ? sections : []
  }

  const results =
    selectedReport.results?.final_report ||  // Primary location following VeraDoc pattern
    selectedReport.content ||
    ""
  
  const sections = getSections(selectedReport)

  // Show all sections
  const sectionsWithSources = sections

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}

      {/* Render sections if present */}
      {sectionsWithSources.length > 0 && (
        <div style={{marginTop: '2rem'}}>
          <h3 style={{fontSize: '1.2rem', marginBottom: '1rem', fontWeight: 'bold'}}>
            Report Sections
          </h3>
          {sectionsWithSources.map((section: any, index: number) => (
            <div key={index} style={{marginBottom: '1.5rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '8px'}}>
              <h4 style={{fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.5rem'}}>
                Section {index + 1}: {section.title || 'Untitled Section'}
              </h4>
              <div style={{backgroundColor: '#f5f5f5', padding: '1rem', borderRadius: '4px'}}>
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                  {section.content || 'No content available'}
                </ReactMarkdown>
              </div>
              {section.source_citations && section.source_citations.length > 0 && (
                <div style={{marginTop: '0.5rem'}}>
                  <button
                    onClick={() => toggleCitations(index)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#0066cc',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      textDecoration: 'underline',
                      padding: 0
                    }}
                  >
                    <strong>Sources:</strong> {section.source_citations.length} citation(s) 
                    {expandedCitations[index] ? ' ▼' : ' ▶'}
                  </button>
                  
                  {expandedCitations[index] && (
                    <div style={{
                      marginTop: '0.5rem',
                      padding: '0.75rem',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '4px',
                      border: '1px solid #e9ecef'
                    }}>
                      {section.source_citations.map((citation: any, citationIndex: number) => (
                        <div key={citationIndex} style={{
                          marginBottom: citationIndex < section.source_citations.length - 1 ? '0.75rem' : '0',
                          paddingBottom: citationIndex < section.source_citations.length - 1 ? '0.75rem' : '0',
                          borderBottom: citationIndex < section.source_citations.length - 1 ? '1px solid #dee2e6' : 'none'
                        }}>
                          <div style={{fontSize: '0.85rem', fontWeight: 'bold', color: '#495057', marginBottom: '0.25rem'}}>
                            Source {citationIndex + 1}: {citation.source || 'Unknown Source'}
                          </div>
                          {citation.page && (
                            <div style={{fontSize: '0.8rem', color: '#6c757d', marginBottom: '0.25rem'}}>
                              Page: {citation.page}
                            </div>
                          )}
                          {citation.scan_type && (
                            <div style={{fontSize: '0.8rem', color: '#6c757d', marginBottom: '0.25rem'}}>
                              Type: {citation.scan_type === 'full_text' ? 'Full Document Scan' : 'Vector Search'}
                            </div>
                          )}
                          {citation.content && (
                            <div style={{
                              fontSize: '0.8rem',
                              color: '#495057',
                              backgroundColor: '#ffffff',
                              padding: '0.5rem',
                              borderRadius: '3px',
                              fontStyle: 'italic',
                              border: '1px solid #e9ecef'
                            }}>
                              "{citation.content}"
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  )
}

export default ReportgenieResults
