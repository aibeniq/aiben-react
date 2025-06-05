import React from "react"
import BaseResultsContainer from "../../components/Archive/BaseResultsContainer"
import ToolTab from "../../components/Archive/ToolTab"
import VeradocResults from "../../components/Archive/Results/VeradocResults"
import ReportgenieResults from "../../components/Archive/Results/ReportgenieResults"
import TwincheckResults from "../../components/Archive/Results/TwincheckResults"
import FormconnectResults from "../../components/Archive/Results/FormconnectResults"
import { useToolArchive } from "../../hooks/useToolArchive"
import useCustomToast from "../../hooks/useCustomToast"
import { createFileRoute } from "@tanstack/react-router"
import { Box, Container, VStack, Tabs } from "@chakra-ui/react"
import { FiCheckCircle, FiFilePlus } from "react-icons/fi"
import { FaBalanceScale } from "react-icons/fa"
import { TbPlugConnected } from "react-icons/tb"

export const Route = createFileRoute("/_layout/archive")({
  component: Archive,
})

function Archive() {
  const {
    veradoc,
    reportgenie,
    twincheck,
    formconnect,
    activeTab,
    setActiveTab,
    copySuccess,
    setCopySuccess,
    loadingDownload,
    setLoadingDownload,
  } = useToolArchive()

  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Copy and download functions
  const handleCopyReport = async () => {
    const selectedReport = getSelectedReport()
    if (!selectedReport) return

    try {
      let fullText = ""

      if (activeTab === "review" && veradoc.selectedReport) {
        fullText = `# Evaluation Summary\n\n${veradoc.selectedReport.results.final_evaluation || ""}\n\n# Question-Answer Details\n\n`
        const qaPairs = veradoc.selectedReport.results.qa_pairs || []
        qaPairs.forEach((pair: any, index: number) => {
          fullText += `## Question ${index + 1}: ${pair.question}\n\n`
          fullText += `### Answer\n${pair.answer}\n\n`
          fullText += `### Relevant Policy Context\n${pair.context}\n\n`
        })
      } else if (activeTab === "generate" && reportgenie.selectedReport) {
        fullText =
          reportgenie.selectedReport.results?.full_report ||
          reportgenie.selectedReport.full_report ||
          reportgenie.selectedReport.content ||
          ""
      } else if (activeTab === "compare" && twincheck.selectedReport) {
        fullText = `# Summary\n\n${twincheck.selectedReport.results?.summary || ""}\n\n# Topic Analysis\n\n`
        const topicResults = twincheck.selectedReport.results?.topic_analysis || []
        topicResults.forEach((topic: any) => {
          fullText += `## Topic: ${topic.topic}\n\n${topic.analysis}\n\n`
        })
      } else if (activeTab === "match" && formconnect.selectedReport) {
        fullText =
          formconnect.selectedReport.results?.comparison ||
          formconnect.selectedReport.results?.message ||
          ""
      }

      await navigator.clipboard.writeText(fullText)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
      showSuccessToast("Report copied to clipboard")
    } catch (err) {
      console.error("Failed to copy report:", err)
      const errorMessage = err instanceof Error ? err.message : "Unknown error"
      showErrorToast(`Failed to copy report to clipboard: ${errorMessage}`)
    }
  }

  const handleDownloadReport = async () => {
    showErrorToast("Download functionality not implemented yet")
  }

  const getSelectedReport = () => {
    switch (activeTab) {
      case "review":
        return veradoc.selectedReport
      case "generate":
        return reportgenie.selectedReport
      case "compare":
        return twincheck.selectedReport
      case "match":
        return formconnect.selectedReport
      default:
        return null
    }
  }

  const components = {
    table: (props: any) => (
      <Box
        as="table"
        width="full"
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        {...props}
      />
    ),
    thead: (props: any) => <Box as="thead" bg="gray.100" {...props} />,
    tbody: (props: any) => <Box as="tbody" {...props} />,
    tr: (props: any) => <Box as="tr" {...props} />,
    th: (props: any) => (
      <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
    ),
    td: (props: any) => <Box as="td" p={4} borderBottomWidth="1px" {...props} />,
  }

  const renderToolResults = () => {
    switch (activeTab) {
      case "review":
        return veradoc.selectedReport ? (
          <VeradocResults selectedReport={veradoc.selectedReport} components={components} />
        ) : null
      case "generate":
        return reportgenie.selectedReport ? (
          <ReportgenieResults selectedReport={reportgenie.selectedReport} components={components} />
        ) : null
      case "compare":
        return twincheck.selectedReport ? (
          <TwincheckResults selectedReport={twincheck.selectedReport} components={components} />
        ) : null
      case "match":
        return formconnect.selectedReport ? (
          <FormconnectResults selectedReport={formconnect.selectedReport} components={components} />
        ) : null
      default:
        return null
    }
  }

  const renderResults = () => {
    const selectedReport = getSelectedReport()
    if (!selectedReport) return null

    return (
      <BaseResultsContainer
        selectedReport={selectedReport}
        copySuccess={copySuccess}
        loadingDownload={loadingDownload}
        onCopyReport={handleCopyReport}
        onDownloadReport={handleDownloadReport}
        onFeedbackSubmitted={(type) => {
          showSuccessToast(`Thank you for marking this response as ${type}!`)
        }}
      >
        {renderToolResults()}
      </BaseResultsContainer>
    )
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Tabs.Root value={activeTab} onValueChange={(e) => setActiveTab(e.value)}>
          <Tabs.List>
            <Tabs.Trigger value="review">
              <FiCheckCircle />
              Review
            </Tabs.Trigger>
            <Tabs.Trigger value="generate">
              <FiFilePlus />
              Generate
            </Tabs.Trigger>
            <Tabs.Trigger value="compare">
              <FaBalanceScale />
              Compare
            </Tabs.Trigger>
            <Tabs.Trigger value="match">
              <TbPlugConnected />
              Match
            </Tabs.Trigger>
          </Tabs.List>

          <Tabs.Content value="review">
            <ToolTab
              reportHistory={veradoc.history}
              selectedHistoryReport={veradoc.selectedReport}
              isHistoryLoading={veradoc.isLoading}
              onLoadReport={veradoc.loadReport}
              emptyMessage="No previous evaluations"
            >
              {renderResults()}
            </ToolTab>
          </Tabs.Content>

          <Tabs.Content value="generate">
            <ToolTab
              reportHistory={reportgenie.history}
              selectedHistoryReport={reportgenie.selectedReport}
              isHistoryLoading={reportgenie.isLoading}
              onLoadReport={reportgenie.loadReport}
              emptyMessage="No previous reports"
            >
              {renderResults()}
            </ToolTab>
          </Tabs.Content>

          <Tabs.Content value="compare">
            <ToolTab
              reportHistory={twincheck.history}
              selectedHistoryReport={twincheck.selectedReport}
              isHistoryLoading={twincheck.isLoading}
              onLoadReport={twincheck.loadReport}
              emptyMessage="No previous comparisons"
            >
              {renderResults()}
            </ToolTab>
          </Tabs.Content>

          <Tabs.Content value="match">
            <ToolTab
              reportHistory={formconnect.history}
              selectedHistoryReport={formconnect.selectedReport}
              isHistoryLoading={formconnect.isLoading}
              onLoadReport={formconnect.loadReport}
              emptyMessage="No previous form processing"
            >
              {renderResults()}
            </ToolTab>
          </Tabs.Content>
        </Tabs.Root>
      </VStack>
    </Container>
  )
}
