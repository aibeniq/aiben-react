import { HStack, Text, VStack } from "@chakra-ui/react"
import { useTranslation } from "react-i18next"
import { Radio, RadioGroup } from "../ui/radio"
import HelpTooltip from "../ui/help-tooltip"

interface SearchModeToggleProps {
  searchMode: "vector" | "full_scan"
  onSearchModeChange: (mode: "vector" | "full_scan") => void
  isDisabled?: boolean
  helpKey?: string // Optional help key for tooltip
}

const SearchModeToggle = ({
  searchMode,
  onSearchModeChange,
  isDisabled = false,
  helpKey,
}: SearchModeToggleProps) => {
  const { t } = useTranslation()

  return (
    <VStack align="stretch" gap={2}>
      <HStack align="center">
        <Text fontSize="sm" fontWeight="medium">
          {t("review.searchMode")}
        </Text>
        {helpKey && <HelpTooltip helpKey={helpKey} />}
      </HStack>
      <RadioGroup
        onValueChange={(details) => onSearchModeChange(details.value as "vector" | "full_scan")}
        value={searchMode}
        disabled={isDisabled}
      >
        <HStack gap={4}>
          <Radio value="vector">{t("review.vectorSearch")}</Radio>
          <Radio value="full_scan">{t("review.fullDocumentScan")}</Radio>
        </HStack>
      </RadioGroup>
      <Text fontSize="xs" color="gray.500">
        {searchMode === "vector"
          ? t("review.vectorSearchDescription")
          : t("review.fullScanDescription")}
      </Text>
    </VStack>
  )
}

export default SearchModeToggle
