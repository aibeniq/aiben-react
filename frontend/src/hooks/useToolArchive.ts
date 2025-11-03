import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import {
  FormconnectService,
  type GetVeradocDetailApiV1VeradocHistoryReportIdGetResponse,
  ReportgenieService,
  TwincheckService,
  VeradocService,
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
  deleteReport?: (reportId: string) => Promise<void>
}

interface UseToolArchiveReturn {
  veradoc: ToolState<
    { [key: string]: unknown },
    GetVeradocDetailApiV1VeradocHistoryReportIdGetResponse
  > &
    ToolActions
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
  const { t } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Veradoc (Review) state
  const [veradocHistory, setVeradocHistory] = useState<
    { [key: string]: unknown }[]
  >([])
  const [selectedVeradocReport, setSelectedVeradocReport] =
    useState<GetVeradocDetailApiV1VeradocHistoryReportIdGetResponse | null>(
      null,
    )
  const [isVeradocLoading, setIsVeradocLoading] = useState(false)

  // ReportGenie (Generate) state
  const [reportgenieHistory, setReportgenieHistory] = useState<
    { [key: string]: unknown }[]
  >([])
  const [selectedReportgenieReport, setSelectedReportgenieReport] =
    useState<any>(null)

  // Prevent unused variable warning for setSelectedReportgenieReport
  if (false) setSelectedReportgenieReport(null)
  const [isReportgenieLoading, setIsReportgenieLoading] = useState(false)

  // TwinCheck (Compare) state
  const [twincheckHistory, setTwincheckHistory] = useState<
    { [key: string]: unknown }[]
  >([])
  const [selectedTwincheckReport, setSelectedTwincheckReport] =
    useState<any>(null)
  const [isTwincheckLoading, setIsTwincheckLoading] = useState(false)

  // FormConnect (Match) state
  const [formconnectHistory, setFormconnectHistory] = useState<
    { [key: string]: unknown }[]
  >([])
  const [selectedFormconnectReport, setSelectedFormconnectReport] =
    useState<any>(null)
  const [isFormconnectLoading, setIsFormconnectLoading] = useState(false)

  // UI state
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [activeTab, setActiveTabInternal] = useState("review")
  const [showAllUsers, setShowAllUsers] = useState(false)

  // Wrapper for setActiveTab to log state changes
  const setActiveTab = (newTab: string) => {
    console.log(
      `Setting active tab to ${newTab}, showAllUsers is currently: ${showAllUsers}`,
    )
    setActiveTabInternal(newTab)
  }

  // Toggle handler for showing all users
  const toggleShowAllUsers = () => {
    console.log("All Users toggle clicked. New value:", !showAllUsers)
    setShowAllUsers((prev) => !prev)
  }

  // Veradoc history query
  const veradocHistoryQuery = useQuery({
    queryKey: ["veradocHistory", showAllUsers],
    queryFn: async () => {
      const response = await VeradocService.getVeradocHistory({
        limit: 20,
        showAll: showAllUsers,
      })
      return response
    },
    enabled: true,
  })

  // ReportGenie history query
  const reportgenieHistoryQuery = useQuery({
    queryKey: ["reportgenieHistory", showAllUsers],
    queryFn: async () => {
      console.log(
        "🔄 REPORTGENIE: Starting to fetch history, showAllUsers:",
        showAllUsers,
      )
      const response = await ReportgenieService.getReportHistory({
        limit: 20,
        showAll: showAllUsers,
      })
      console.log(
        "✅ REPORTGENIE: History fetch completed, response:",
        response,
      )
      console.log(
        "📊 REPORTGENIE: Number of reports returned:",
        Array.isArray(response) ? response.length : "Response is not an array",
      )
      if (Array.isArray(response) && response.length > 0) {
        console.log("📋 REPORTGENIE: First report sample:", response[0])
      }
      return response
    },
    enabled: true, // Enabled now that backend method is available
  })

  // TwinCheck history query
  const twincheckHistoryQuery = useQuery({
    queryKey: ["twincheckHistory", showAllUsers],
    queryFn: async () => {
      const response = await TwincheckService.getComparisonHistory({
        limit: 20,
        showAll: showAllUsers,
      })
      return response
    },
    enabled: true,
  })

  // FormConnect history query
  const formconnectHistoryQuery = useQuery({
    queryKey: ["formconnectHistory", showAllUsers],
    queryFn: async () => {
      console.log(
        "🔄 FORMCONNECT: Starting to fetch history, showAllUsers:",
        showAllUsers,
      )
      const response = await FormconnectService.getFormHistory({
        limit: 20,
        showAll: showAllUsers,
      })
      console.log(
        "✅ FORMCONNECT: History fetch completed, response:",
        response,
      )
      console.log(
        "📊 FORMCONNECT: Number of records returned:",
        Array.isArray(response) ? response.length : "Response is not an array",
      )
      if (Array.isArray(response) && response.length > 0) {
        console.log("📋 FORMCONNECT: First record sample:", response[0])
      }
      return response
    },
    enabled: true,
  })

  // Update states when queries change
  useEffect(() => {
    if (veradocHistoryQuery.data) {
      setVeradocHistory(
        Array.isArray(veradocHistoryQuery.data) ? veradocHistoryQuery.data : [],
      )
    }
    setIsVeradocLoading(veradocHistoryQuery.isLoading)
  }, [veradocHistoryQuery.data, veradocHistoryQuery.isLoading])

  useEffect(() => {
    console.log(
      "🔄 REPORTGENIE: useEffect triggered for reportgenieHistoryQuery",
    )
    console.log(
      "📊 REPORTGENIE: Query status - isLoading:",
      reportgenieHistoryQuery.isLoading,
      "isError:",
      reportgenieHistoryQuery.isError,
      "error:",
      reportgenieHistoryQuery.error,
    )

    if (reportgenieHistoryQuery.data) {
      console.log(
        "✅ REPORTGENIE: Setting history data:",
        reportgenieHistoryQuery.data,
      )
      setReportgenieHistory(
        Array.isArray(reportgenieHistoryQuery.data)
          ? reportgenieHistoryQuery.data
          : [],
      )
    } else {
      console.log("❌ REPORTGENIE: No data received or data is null/undefined")
    }
    setIsReportgenieLoading(reportgenieHistoryQuery.isLoading)
  }, [reportgenieHistoryQuery.data, reportgenieHistoryQuery.isLoading])

  useEffect(() => {
    if (twincheckHistoryQuery.data) {
      setTwincheckHistory(
        Array.isArray(twincheckHistoryQuery.data)
          ? twincheckHistoryQuery.data
          : [],
      )
    }
    setIsTwincheckLoading(twincheckHistoryQuery.isLoading)
  }, [twincheckHistoryQuery.data, twincheckHistoryQuery.isLoading])

  useEffect(() => {
    console.log(
      "🔄 FORMCONNECT: useEffect triggered for formconnectHistoryQuery",
    )
    console.log(
      "📊 FORMCONNECT: Query status - isLoading:",
      formconnectHistoryQuery.isLoading,
      "isError:",
      formconnectHistoryQuery.isError,
    )
    if (formconnectHistoryQuery.error) {
      console.log("❌ FORMCONNECT: Error:", formconnectHistoryQuery.error)
    }

    if (formconnectHistoryQuery.data) {
      console.log(
        "✅ FORMCONNECT: Setting history data:",
        formconnectHistoryQuery.data,
      )
      setFormconnectHistory(
        Array.isArray(formconnectHistoryQuery.data)
          ? formconnectHistoryQuery.data
          : [],
      )
    } else {
      console.log("❌ FORMCONNECT: No data received or data is null/undefined")
    }
    setIsFormconnectLoading(formconnectHistoryQuery.isLoading)
  }, [formconnectHistoryQuery.data, formconnectHistoryQuery.isLoading])

  // Load functions for each tool
  const loadVeradocReport = async (reportId: string) => {
    try {
      setIsVeradocLoading(true)

      // Load summary with question headers (expandable sections)
      const summary = await VeradocService.getVeradocDetail({
        reportId,
        includeQaPairs: false, // Fast: ~2KB, includes qa_pairs_summary with question headers
      })
      setSelectedVeradocReport(summary)
      setIsVeradocLoading(false) // Show summary and question headers immediately
      showSuccessToast(t("archive.successMessages.evaluationLoaded"))

      // Note: Individual QA pairs will be loaded on-demand when user clicks to expand a question
      // This provides true lazy loading - only fetch what the user actually wants to see
    } catch (error) {
      console.error("Error loading report:", error)
      showErrorToast(t("toast.evaluationLoadFailed"))
      setIsVeradocLoading(false)
    }
  }

  const loadReportgenieReport = async (reportId: string) => {
    try {
      setIsReportgenieLoading(true)

      // Load summary only (no sections)
      const summary = await ReportgenieService.getReportDetail({
        reportId,
        // includeSections: false,  // Parameter not supported in current API
      })
      setSelectedReportgenieReport(summary)
      setIsReportgenieLoading(false) // Show summary immediately
      showSuccessToast(t("archive.successMessages.reportLoaded"))

      // Note: Sections should be loaded on-demand when user requests them
    } catch (error) {
      console.error("Error loading report:", error)
      showErrorToast(t("toast.reportLoadFailed"))
      setIsReportgenieLoading(false)
    }
  }

  const loadTwincheckReport = async (comparisonId: string) => {
    try {
      setIsTwincheckLoading(true)
      const report = await TwincheckService.getComparisonDetail({
        comparisonId,
      })
      setSelectedTwincheckReport(report)
      showSuccessToast(t("archive.successMessages.comparisonLoaded"))
    } catch (error) {
      console.error("Error loading comparison:", error)
      showErrorToast(t("toast.comparisonLoadFailed"))
    } finally {
      setIsTwincheckLoading(false)
    }
  }

  const loadFormconnectReport = async (interactionId: string) => {
    try {
      setIsFormconnectLoading(true)
      const report = await FormconnectService.getFormDetail({ interactionId })
      setSelectedFormconnectReport(report)
      showSuccessToast(t("archive.successMessages.formProcessingLoaded"))
    } catch (error) {
      console.error("Error loading form processing:", error)
      showErrorToast(t("toast.formProcessingLoadFailed"))
    } finally {
      setIsFormconnectLoading(false)
    }
  }

  // Delete functions for each tool
  const deleteVeradocReport = async (reportId: string) => {
    try {
      await VeradocService.deleteEvaluation({ evaluationId: reportId })
      showSuccessToast(t("archive.successMessages.evaluationDeleted"))

      // Clear selected report if it was the one being deleted
      if (selectedVeradocReport?.id === reportId) {
        setSelectedVeradocReport(null)
      }

      // Refresh the history
      veradocHistoryQuery.refetch()
    } catch (error) {
      console.error("Error deleting evaluation:", error)
      showErrorToast(t("toast.evaluationDeleteFailed"))
    }
  }

  const deleteReportgenieReport = async (reportId: string) => {
    try {
      await ReportgenieService.deleteReport({ reportId })
      showSuccessToast(t("archive.successMessages.reportDeleted"))

      // Clear selected report if it was the one being deleted
      if (selectedReportgenieReport?.id === reportId) {
        setSelectedReportgenieReport(null)
      }

      // Refresh the history
      reportgenieHistoryQuery.refetch()
    } catch (error) {
      console.error("Error deleting report:", error)
      showErrorToast(t("toast.reportDeleteFailed"))
    }
  }

  const deleteTwincheckReport = async (comparisonId: string) => {
    try {
      await TwincheckService.deleteComparison({ comparisonId })
      showSuccessToast(t("archive.successMessages.comparisonDeleted"))

      // Clear selected report if it was the one being deleted
      if (selectedTwincheckReport?.id === comparisonId) {
        setSelectedTwincheckReport(null)
      }

      // Refresh the history
      twincheckHistoryQuery.refetch()
    } catch (error) {
      console.error("Error deleting comparison:", error)
      showErrorToast(t("toast.comparisonDeleteFailed"))
    }
  }

  const deleteFormconnectReport = async (interactionId: string) => {
    try {
      await FormconnectService.deleteForm({ formId: interactionId })
      showSuccessToast(t("archive.successMessages.formProcessingDeleted"))

      // Clear selected report if it was the one being deleted
      if (selectedFormconnectReport?.id === interactionId) {
        setSelectedFormconnectReport(null)
      }

      // Refresh the history
      formconnectHistoryQuery.refetch()
    } catch (error) {
      console.error("Error deleting form processing:", error)
      showErrorToast(t("toast.formProcessingDeleteFailed"))
    }
  }

  return {
    veradoc: {
      history: veradocHistory,
      selectedReport: selectedVeradocReport,
      isLoading: isVeradocLoading,
      loadReport: loadVeradocReport,
      deleteReport: deleteVeradocReport,
    },
    reportgenie: {
      history: reportgenieHistory,
      selectedReport: selectedReportgenieReport,
      isLoading: isReportgenieLoading,
      loadReport: loadReportgenieReport,
      deleteReport: deleteReportgenieReport,
    },
    twincheck: {
      history: twincheckHistory,
      selectedReport: selectedTwincheckReport,
      isLoading: isTwincheckLoading,
      loadReport: loadTwincheckReport,
      deleteReport: deleteTwincheckReport,
    },
    formconnect: {
      history: formconnectHistory,
      selectedReport: selectedFormconnectReport,
      isLoading: isFormconnectLoading,
      loadReport: loadFormconnectReport,
      deleteReport: deleteFormconnectReport,
    },
    activeTab,
    setActiveTab,
    copySuccess,
    setCopySuccess,
    loadingDownload,
    setLoadingDownload,
    showAllUsers,
    toggleShowAllUsers,
  }
}
