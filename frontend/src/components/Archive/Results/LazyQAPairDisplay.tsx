import { Box, Button, Spinner, Text } from "@chakra-ui/react"
import { useState } from "react"
import type React from "react"
import { useTranslation } from "react-i18next"
import { VeradocService } from "../../../client"
import useCustomToast from "../../../hooks/useCustomToast"
import QAPairDisplay from "../Utils/QAPairDisplay"

interface QaPairSummary {
  index: number
  question: string
}

interface LazyQAPairDisplayProps {
  reportId: string
  qaPairSummary: QaPairSummary
}

const LazyQAPairDisplay: React.FC<LazyQAPairDisplayProps> = ({ reportId, qaPairSummary }) => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [qaPairDetail, setQaPairDetail] = useState<any>(null)
  const { showErrorToast } = useCustomToast()

  const handleToggle = async () => {
    if (!isOpen && !qaPairDetail) {
      // First time opening - load the QA pair details
      setIsLoading(true)
      try {
        const detail = await VeradocService.getVeradocQaPair({
          reportId,
          qaIndex: qaPairSummary.index,
        })
        setQaPairDetail(detail)
        setIsOpen(true)
      } catch (error) {
        console.error("Error loading QA pair:", error)
        showErrorToast("Failed to load question details")
      } finally {
        setIsLoading(false)
      }
    } else {
      // Just toggle the accordion
      setIsOpen(!isOpen)
    }
  }

  return (
    <Box
      borderWidth="1px"
      borderRadius="md"
      p={4}
      mb={3}
      bg={isOpen ? "gray.50" : "white"}
      _dark={{ bg: isOpen ? "gray.700" : "gray.800" }}
    >
      <Button
        onClick={handleToggle}
        variant="ghost"
        width="100%"
        justifyContent="flex-start"
        fontWeight="semibold"
        fontSize="md"
        _hover={{ bg: "gray.100", _dark: { bg: "gray.600" } }}
      >
        <Box flex="1" textAlign="left">
          <Text>
            {t("common.questionNumber", { number: qaPairSummary.index + 1 })}{" "}
            {qaPairSummary.question}
          </Text>
        </Box>
        {isLoading && <Spinner size="sm" ml={2} />}
        {!isLoading && (
          <Text ml={2} color="gray.500">
            {isOpen ? "▼" : "▶"}
          </Text>
        )}
      </Button>

      {isOpen && qaPairDetail && (
        <Box mt={4}>
          <QAPairDisplay pair={qaPairDetail} index={qaPairSummary.index} />
        </Box>
      )}
    </Box>
  )
}

export default LazyQAPairDisplay
