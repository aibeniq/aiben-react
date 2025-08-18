import React, { createContext, useContext, useState, ReactNode } from 'react'

interface ReviewResult {
  filename: string
  displayResults: string
  qaPairs: any[]
  interactionId?: string
}

interface GenerateResult {
  full_report: string
  sections: any[]
  interactionId?: string
}

interface CompareResult {
  summary: string
  topicResults: any[]
  interactionId?: string
}

interface MatchResult {
  results: string
  interactionId?: string
}

interface ResultsContextType {
  // Review tab results
  reviewResults: ReviewResult[]
  setReviewResults: (results: ReviewResult[]) => void
  reviewActiveTab: number
  setReviewActiveTab: (tab: number) => void
  clearReviewResults: () => void

  // Generate tab results
  generateResult: GenerateResult | null
  setGenerateResult: (result: GenerateResult | null) => void
  clearGenerateResult: () => void

  // Compare tab results
  compareResult: CompareResult | null
  setCompareResult: (result: CompareResult | null) => void
  clearCompareResult: () => void

  // Match tab results
  matchResult: MatchResult | null
  setMatchResult: (result: MatchResult | null) => void
  clearMatchResult: () => void
}

const ResultsContext = createContext<ResultsContextType | undefined>(undefined)

export const useResults = () => {
  const context = useContext(ResultsContext)
  if (context === undefined) {
    throw new Error('useResults must be used within a ResultsProvider')
  }
  return context
}

export const ResultsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Review state
  const [reviewResults, setReviewResults] = useState<ReviewResult[]>([])
  const [reviewActiveTab, setReviewActiveTab] = useState<number>(0)

  // Generate state
  const [generateResult, setGenerateResult] = useState<GenerateResult | null>(null)

  // Compare state
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null)

  // Match state
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)

  const clearReviewResults = () => {
    setReviewResults([])
    setReviewActiveTab(0)
  }

  const clearGenerateResult = () => {
    setGenerateResult(null)
  }

  const clearCompareResult = () => {
    setCompareResult(null)
  }

  const clearMatchResult = () => {
    setMatchResult(null)
  }

  return (
    <ResultsContext.Provider
      value={{
        reviewResults,
        setReviewResults,
        reviewActiveTab,
        setReviewActiveTab,
        clearReviewResults,
        generateResult,
        setGenerateResult,
        clearGenerateResult,
        compareResult,
        setCompareResult,
        clearCompareResult,
        matchResult,
        setMatchResult,
        clearMatchResult,
      }}
    >
      {children}
    </ResultsContext.Provider>
  )
}
