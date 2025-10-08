import type React from "react"
import { type ReactNode, createContext, useContext, useState } from "react"

// Vision analysis metadata interface
interface VisionAnalysisMetadata {
  hasVisionAnalysis: boolean
  imageCount: number
  sourceFiles: string[]
  visionModel?: string
}

interface ReviewResult {
  filename: string
  displayResults: string
  qaPairs: any[]
  interactionId?: string
  visionMetadata?: VisionAnalysisMetadata
}

interface GenerateResult {
  full_report: string
  sections: any[]
  interactionId?: string
  visionMetadata?: VisionAnalysisMetadata
}

interface CompareResult {
  summary: string
  topicResults: Array<{
    topic: string
    analysis: string
    visionMetadata?: VisionAnalysisMetadata
  }>
  interactionId?: string
}

interface MatchResult {
  results: string
  interactionId?: string
  visionMetadata?: VisionAnalysisMetadata
}

// Input parameter interfaces
interface ReviewInputs {
  selectedKnowledgeBase: any | null
  selectedChecklist: any | null
  questions: string
  customInstructions: string
  searchMode: "vector" | "full_scan"
  fileItems: any[]
}

interface GenerateInputs {
  selectedKnowledgeBase: any | null
  selectedOutline: any | null
  sections: string
  customInstructions: string
  searchMode: "vector" | "full_scan"
}

interface CompareInputs {
  document1: File | null
  document2: File | null
  topics: string
  selectedComparison: any | null
}

interface MatchInputs {
  fileItems: any[]
  selectedForm: any | null
  fields: string
  searchMode: "vector" | "full_scan"
}

interface ResultsContextType {
  // Review tab results
  reviewResults: ReviewResult[]
  setReviewResults: (results: ReviewResult[]) => void
  reviewActiveTab: number
  setReviewActiveTab: (tab: number) => void
  clearReviewResults: () => void

  // Review tab inputs
  reviewInputs: ReviewInputs | null
  setReviewInputs: (inputs: ReviewInputs | null) => void

  // Generate tab results
  generateResult: GenerateResult | null
  setGenerateResult: (result: GenerateResult | null) => void
  clearGenerateResult: () => void

  // Generate tab inputs
  generateInputs: GenerateInputs | null
  setGenerateInputs: (inputs: GenerateInputs | null) => void

  // Compare tab results
  compareResult: CompareResult | null
  setCompareResult: (result: CompareResult | null) => void
  clearCompareResult: () => void

  // Compare tab inputs
  compareInputs: CompareInputs | null
  setCompareInputs: (inputs: CompareInputs | null) => void

  // Match tab results
  matchResult: MatchResult | null
  setMatchResult: (result: MatchResult | null) => void
  clearMatchResult: () => void

  // Match tab inputs
  matchInputs: MatchInputs | null
  setMatchInputs: (inputs: MatchInputs | null) => void
}

const ResultsContext = createContext<ResultsContextType | undefined>(undefined)

export const useResults = () => {
  const context = useContext(ResultsContext)
  if (context === undefined) {
    throw new Error("useResults must be used within a ResultsProvider")
  }
  return context
}

export const ResultsProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  // Review state
  const [reviewResults, setReviewResults] = useState<ReviewResult[]>([])
  const [reviewActiveTab, setReviewActiveTab] = useState<number>(0)
  const [reviewInputs, setReviewInputs] = useState<ReviewInputs | null>(null)

  // Generate state
  const [generateResult, setGenerateResult] = useState<GenerateResult | null>(
    null,
  )
  const [generateInputs, setGenerateInputs] = useState<GenerateInputs | null>(
    null,
  )

  // Compare state
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null)
  const [compareInputs, setCompareInputs] = useState<CompareInputs | null>(null)

  // Match state
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [matchInputs, setMatchInputs] = useState<MatchInputs | null>(null)

  const clearReviewResults = () => {
    setReviewResults([])
    setReviewActiveTab(0)
    setReviewInputs(null)
  }

  const clearGenerateResult = () => {
    setGenerateResult(null)
    setGenerateInputs(null)
  }

  const clearCompareResult = () => {
    setCompareResult(null)
    setCompareInputs(null)
  }

  const clearMatchResult = () => {
    setMatchResult(null)
    setMatchInputs(null)
  }

  return (
    <ResultsContext.Provider
      value={{
        reviewResults,
        setReviewResults,
        reviewActiveTab,
        setReviewActiveTab,
        clearReviewResults,
        reviewInputs,
        setReviewInputs,
        generateResult,
        setGenerateResult,
        clearGenerateResult,
        generateInputs,
        setGenerateInputs,
        compareResult,
        setCompareResult,
        clearCompareResult,
        compareInputs,
        setCompareInputs,
        matchResult,
        setMatchResult,
        clearMatchResult,
        matchInputs,
        setMatchInputs,
      }}
    >
      {children}
    </ResultsContext.Provider>
  )
}
