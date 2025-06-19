import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import {
  VeradocGetVeradocDetailResponse,
  VeradocService,
  ReportgenieService,
  TwincheckService,
  FormconnectService,
} from "../client"
import useCustomToast from "./useCustomToast"

// Types for each tool's data
interface ToolState<THistory = any, TDetail = any> {
  history: THistory[]
  selectedReport: TDetail | null
  isLoading: boolean
}

interface ToolActions {
  loadReport: (reportId: string) => Promise<void>
}

interface UseToolArchiveReturn {
  veradoc: ToolState<{ [key: string]: unknown }, VeradocGetVeradocDetailResponse> & ToolActions
  reportgenie: ToolState<{ [key: string]: unknown }, any> & ToolActions
  twincheck: ToolState<{ [key: string]: unknown }, any> & ToolActions
  formconnect: ToolState<{ [key: string]: unknown }, any> & ToolActions
  activeTab: string
  setActiveTab: (tab: string) => void
  copySuccess: boolean
  setCopySuccess: (success: boolean) => void
  loadingDownload: boolean
  setLoadingDownload: (loading: boolean) => void
  showAllUsers: boolean
  toggleShowAllUsers: () => void
}

export const useToolArchive = (): UseToolArchiveReturn => {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Veradoc (Review) state
  const [veradocHistory, setVeradocHistory] = useState<{ [key: string]: unknown }[]>([])
  const [selectedVeradocReport, setSelectedVeradocReport] =
    useState<VeradocGetVeradocDetailResponse | null>(null)
  const [isVeradocLoading, setIsVeradocLoading] = useState(false)

  // ReportGenie (Generate) state
  const [reportgenieHistory, setReportgenieHistory] = useState<{ [key: string]: unknown }[]>([])
  const [selectedReportgenieReport, setSelectedReportgenieReport] = useState<any>(null)
  const [isReportgenieLoading, setIsReportgenieLoading] = useState(false)

  // TwinCheck (Compare) state
  const [twincheckHistory, setTwincheckHistory] = useState<{ [key: string]: unknown }[]>([])
  const [selectedTwincheckReport, setSelectedTwincheckReport] = useState<any>(null)
  const [isTwincheckLoading, setIsTwincheckLoading] = useState(false)

  // FormConnect (Match) state
  const [formconnectHistory, setFormconnectHistory] = useState<{ [key: string]: unknown }[]>([])
  const [selectedFormconnectReport, setSelectedFormconnectReport] = useState<any>(null)
  const [isFormconnectLoading, setIsFormconnectLoading] = useState(false)

  // UI state
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [activeTab, setActiveTabInternal] = useState("review")
  const [showAllUsers, setShowAllUsers] = useState(false)

  // Wrapper for setActiveTab to log state changes
  const setActiveTab = (newTab: string) => {
    console.log(`Setting active tab to ${newTab}, showAllUsers is currently: ${showAllUsers}`);
    setActiveTabInternal(newTab);
  }

  // Toggle handler for showing all users
  const toggleShowAllUsers = () => {
    console.log("All Users toggle clicked. New value:", !showAllUsers);
    setShowAllUsers(prev => !prev);
  }

  // Veradoc history query
  const veradocHistoryQuery = useQuery({
    queryKey: ["veradocHistory", showAllUsers],
    queryFn: async () => {
      const response = await VeradocService.getVeradocHistory({ 
        limit: 20,
        showAll: showAllUsers 
      })
      return response
    },
    enabled: true,
  })

  // ReportGenie history query
  const reportgenieHistoryQuery = useQuery({
    queryKey: ["reportgenieHistory", showAllUsers],
    queryFn: async () => {
      const response = await ReportgenieService.getReportHistory({ 
        limit: 20,
        showAll: showAllUsers 
      })
      return response
    },
    enabled: true,
  })

  // TwinCheck history query
  const twincheckHistoryQuery = useQuery({
    queryKey: ["twincheckHistory", showAllUsers],
    queryFn: async () => {
      const response = await TwincheckService.getComparisonHistory({ 
        limit: 20,
        showAll: showAllUsers 
      })
      return response
    },
    enabled: true,
  })

  // FormConnect history query
  const formconnectHistoryQuery = useQuery({
    queryKey: ["formconnectHistory", showAllUsers],
    queryFn: async () => {
      const response = await FormconnectService.getFormHistory({ 
        limit: 20,
        showAll: showAllUsers 
      })
      return response
    },
    enabled: true,
  })

  // Update states when queries change
  useEffect(() => {
    if (veradocHistoryQuery.data) {
      setVeradocHistory(Array.isArray(veradocHistoryQuery.data) ? veradocHistoryQuery.data : [])
    }
    setIsVeradocLoading(veradocHistoryQuery.isLoading)
  }, [veradocHistoryQuery.data, veradocHistoryQuery.isLoading])

  useEffect(() => {
    if (reportgenieHistoryQuery.data) {
      setReportgenieHistory(
        Array.isArray(reportgenieHistoryQuery.data) ? reportgenieHistoryQuery.data : [],
      )
    }
    setIsReportgenieLoading(reportgenieHistoryQuery.isLoading)
  }, [reportgenieHistoryQuery.data, reportgenieHistoryQuery.isLoading])

  useEffect(() => {
    if (twincheckHistoryQuery.data) {
      setTwincheckHistory(
        Array.isArray(twincheckHistoryQuery.data) ? twincheckHistoryQuery.data : [],
      )
    }
    setIsTwincheckLoading(twincheckHistoryQuery.isLoading)
  }, [twincheckHistoryQuery.data, twincheckHistoryQuery.isLoading])

  useEffect(() => {
    if (formconnectHistoryQuery.data) {
      setFormconnectHistory(
        Array.isArray(formconnectHistoryQuery.data) ? formconnectHistoryQuery.data : [],
      )
    }
    setIsFormconnectLoading(formconnectHistoryQuery.isLoading)
  }, [formconnectHistoryQuery.data, formconnectHistoryQuery.isLoading])

  // Load functions for each tool
  const loadVeradocReport = async (reportId: string) => {
    try {
      setIsVeradocLoading(true)
      const report = await VeradocService.getVeradocDetail({ reportId })
      setSelectedVeradocReport(report)
      showSuccessToast("Evaluation loaded successfully")
    } catch (error) {
      console.error("Error loading report:", error)
      showErrorToast("Failed to load evaluation")
    } finally {
      setIsVeradocLoading(false)
    }
  }

  const loadReportgenieReport = async (reportId: string) => {
    try {
      setIsReportgenieLoading(true)
      const report = await ReportgenieService.getReportDetail({ reportId })
      setSelectedReportgenieReport(report)
      showSuccessToast("Report loaded successfully")
    } catch (error) {
      console.error("Error loading report:", error)
      showErrorToast("Failed to load report")
    } finally {
      setIsReportgenieLoading(false)
    }
  }

  const loadTwincheckReport = async (comparisonId: string) => {
    try {
      setIsTwincheckLoading(true)
      const report = await TwincheckService.getComparisonDetail({ comparisonId })
      setSelectedTwincheckReport(report)
      showSuccessToast("Comparison loaded successfully")
    } catch (error) {
      console.error("Error loading comparison:", error)
      showErrorToast("Failed to load comparison")
    } finally {
      setIsTwincheckLoading(false)
    }
  }

  const loadFormconnectReport = async (interactionId: string) => {
    try {
      setIsFormconnectLoading(true)
      const report = await FormconnectService.getFormDetail({ interactionId })
      setSelectedFormconnectReport(report)
      showSuccessToast("Form processing loaded successfully")
    } catch (error) {
      console.error("Error loading form processing:", error)
      showErrorToast("Failed to load form processing")
    } finally {
      setIsFormconnectLoading(false)
    }
  }

  return {
    veradoc: {
      history: veradocHistory,
      selectedReport: selectedVeradocReport,
      isLoading: isVeradocLoading,
      loadReport: loadVeradocReport,
    },
    reportgenie: {
      history: reportgenieHistory,
      selectedReport: selectedReportgenieReport,
      isLoading: isReportgenieLoading,
      loadReport: loadReportgenieReport,
    },
    twincheck: {
      history: twincheckHistory,
      selectedReport: selectedTwincheckReport,
      isLoading: isTwincheckLoading,
      loadReport: loadTwincheckReport,
    },
    formconnect: {
      history: formconnectHistory,
      selectedReport: selectedFormconnectReport,
      isLoading: isFormconnectLoading,
      loadReport: loadFormconnectReport,
    },
    activeTab,
    setActiveTab,
    copySuccess,
    setCopySuccess,
    loadingDownload,
    setLoadingDownload,
    showAllUsers,
    toggleShowAllUsers
  }
}
