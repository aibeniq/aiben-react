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
import { VeradocService, ReportgenieService, TwincheckService } from "../../client"
import { useState } from "react"

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
    showAllUsers,
    toggleShowAllUsers,
  } = useToolArchive()

  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

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
    const selectedReport = getSelectedReport()
    if (!selectedReport) return

    try {
      setLoadingDownload(true)
      let response
      let fullText = ""

      if (activeTab === "review" && veradoc.selectedReport) {
        // Prepare combined text with evaluation summary and QA pairs
        fullText = `# Evaluation Summary\n\n${veradoc.selectedReport.results.final_evaluation || ""}\n\n# Question-Answer Details\n\n`
        const qaPairs = veradoc.selectedReport.results.qa_pairs || []
        qaPairs.forEach((pair: any, index: number) => {
          fullText += `## Question ${index + 1}: ${pair.question}\n\n`
          fullText += `### Answer\n${pair.answer}\n\n`
          fullText += `### Relevant Policy Context\n${pair.context}\n\n`
        })

        response = await VeradocService.generateDocx({
          requestBody: { content: fullText },
        })
      } else if (activeTab === "generate" && reportgenie.selectedReport) {
        fullText =
          reportgenie.selectedReport.results?.full_report ||
          reportgenie.selectedReport.full_report ||
          reportgenie.selectedReport.content ||
          ""

        response = await ReportgenieService.generateDocx({
          requestBody: { content: fullText },
        })
      } else if (activeTab === "compare" && twincheck.selectedReport) {
        // Prepare combined text with summary and all topic analyses
        fullText = `# Summary\n\n${twincheck.selectedReport.results?.summary || ""}\n\n# Topic Analysis\n\n`
        const topicResults = twincheck.selectedReport.results?.topic_analysis || []
        topicResults.forEach((topic: any) => {
          fullText += `## Topic: ${topic.topic}\n\n${topic.analysis}\n\n`
        })

        response = await TwincheckService.generateDocx({
          requestBody: { content: fullText },
        })
      } else if (activeTab === "match" && formconnect.selectedReport) {
        // FormConnect doesn't have generateDocx, show error message
        showErrorToast("Download functionality is not available for Form Processing results")
        return
      }

      if (!response) return

      // Handle the response blob
      let blob
      if (response instanceof Blob) {
        blob = response
      } else if (response instanceof ArrayBuffer) {
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        blob = new Blob([response as BlobPart], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url

      // Set filename based on tool type
      let filename = ""
      switch (activeTab) {
        case "review":
          filename = `evaluation_${timestamp}.docx`
          break
        case "generate":
          filename = `report_${timestamp}.docx`
          break
        case "compare":
          filename = `comparison_${timestamp}.docx`
          break
        default:
          filename = `document_${timestamp}.docx`
      }

      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast("Document downloaded successfully")
    } catch (err) {
      console.error("Failed to download report:", err)
      const errorMessage = err instanceof Error ? err.message : "Unknown error"
      showErrorToast(`Failed to download document: ${errorMessage}`)
    } finally {
      setLoadingDownload(false)
    }
  }

  // Add CSV download function
  // Add CSV download function
  const handleDownloadCsv = async () => {
    const selectedReport = getSelectedReport()
    if (!selectedReport || activeTab !== "generate") return

    try {
      setLoadingCsvDownload(true)
      console.log("Starting CSV download...")
      console.log("Selected report:", selectedReport)

      // Prepare the sections data for CSV generation
      const csvData = {
        sections: selectedReport.results?.sections || [],
      }
      console.log("CSV data to send:", csvData)
      console.log("Number of sections:", csvData.sections.length)

      const response = await ReportgenieService.generateCsv({
        requestBody: { content: JSON.stringify(csvData) },
      })

      console.log("Received CSV response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)
      console.log("Response instanceof ArrayBuffer:", response instanceof ArrayBuffer)

      // Handle the response blob
      let blob
      if (response instanceof Blob) {
        console.log("Response is already a Blob")
        blob = response
      } else if (response instanceof ArrayBuffer) {
        console.log("Converting ArrayBuffer to Blob")
        blob = new Blob([response], { type: "text/csv" })
      } else {
        console.log("Converting unknown response type to Blob")
        blob = new Blob([response as BlobPart], { type: "text/csv" })
      }

      console.log("Final blob:", blob)
      console.log("Blob size:", blob.size)
      console.log("Blob type:", blob.type)

      // Create download link
      const url = window.URL.createObjectURL(blob)
      console.log("Created object URL:", url)

      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      const filename = `report_${timestamp}.csv`

      a.href = url
      a.download = filename

      console.log("Download filename:", filename)
      console.log("About to trigger download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("Download triggered successfully")
      showSuccessToast("CSV downloaded successfully")
    } catch (err) {
      console.error("Failed to download CSV:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      const errorMessage = err instanceof Error ? err.message : "Unknown error"
      showErrorToast(`Failed to download CSV: ${errorMessage}`)
    } finally {
      console.log("CSV download process completed")
      setLoadingCsvDownload(false)
    }
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
        bg="surface"
        {...props}
      />
    ),
    thead: (props: any) => <Box as="thead" bg="panel" {...props} />,
    tbody: (props: any) => <Box as="tbody" bg="panel" {...props} />,
    tr: (props: any) => <Box as="tr" {...props} />,
    th: (props: any) => (
      <Box
        as="th"
        p={4}
        textAlign="left"
        fontWeight="bold"
        borderBottomWidth="1px"
        bg="panel"
        {...props}
      />
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
        loadingCsvDownload={loadingCsvDownload}
        onCopyReport={handleCopyReport}
        onDownloadReport={handleDownloadReport}
        onDownloadCsv={handleDownloadCsv}
        showCsvDownload={activeTab === "generate"}
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
        <Tabs.Root
          value={activeTab}
          onValueChange={(e) => {
            console.log(
              `Tab changed from ${activeTab} to ${e.value}, showAllUsers is: ${showAllUsers}`,
            )
            setActiveTab(e.value)
          }}
        >
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
              showAllUsers={showAllUsers}
              onToggleShowAllUsers={toggleShowAllUsers}
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
              showAllUsers={showAllUsers}
              onToggleShowAllUsers={toggleShowAllUsers}
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
              showAllUsers={showAllUsers}
              onToggleShowAllUsers={toggleShowAllUsers}
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
              showAllUsers={showAllUsers}
              onToggleShowAllUsers={toggleShowAllUsers}
            >
              {renderResults()}
            </ToolTab>
          </Tabs.Content>
        </Tabs.Root>
      </VStack>
    </Container>
  )
}
