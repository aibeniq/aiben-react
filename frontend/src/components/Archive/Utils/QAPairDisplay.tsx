import { Box, Heading, Text } from "@chakra-ui/react"
import type React from "react"
import { useTranslation } from "react-i18next"
import SourceCitationAccordion from "./SourceCitationAccordion"

interface QAPairDisplayProps {
  pair: any
  index: number
}

const QAPairDisplay: React.FC<QAPairDisplayProps> = ({ pair, index }) => {
  const { t } = useTranslation()
  return (
    <Box mb={4} p={4} borderWidth="1px" borderRadius="md" bg="bg">
      <Heading as="h3" size="md" mb={2}>
        {t("common.questionNumber", { number: index + 1 })} {pair.question}
      </Heading>

      <Box mb={3}>
        <Text fontWeight="bold">{t("common.answer")}</Text>
        <Text>{pair.answer}</Text>
      </Box>

      <Box mb={3}>
        <Text fontWeight="bold">{t("common.relevantPolicyContext")}</Text>
        <Text>{pair.context}</Text>
      </Box>

      {pair.source_citations && pair.source_citations.length > 0 && (
        <SourceCitationAccordion
          sourceCitations={pair.source_citations}
          accordionValue={`item-${index}`}
        />
      )}
    </Box>
  )
}

export default QAPairDisplay
