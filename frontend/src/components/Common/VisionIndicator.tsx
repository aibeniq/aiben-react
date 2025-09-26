import { Badge, HStack, Icon, Text } from "@chakra-ui/react"
import { FiImage, FiEye } from "react-icons/fi"
import { useTranslation } from "react-i18next"

interface VisionIndicatorProps {
  hasVisionAnalysis: boolean
  imageCount?: number
  variant?: "badge" | "inline"
}

export const VisionIndicator = ({
  hasVisionAnalysis,
  imageCount = 0,
  variant = "badge",
}: VisionIndicatorProps) => {
  const { t } = useTranslation()

  if (!hasVisionAnalysis) return null

  if (variant === "badge") {
    return (
      <Badge colorScheme="blue" size="sm">
        <HStack gap={1}>
          <Icon as={FiEye} size={3} />
          <Text fontSize="xs">{t("common.visionAnalysis", "Vision Analysis")}</Text>
        </HStack>
      </Badge>
    )
  }

  return (
    <HStack gap={1} fontSize="xs" color="blue.600">
      <Icon as={FiImage} size={3} />
      <Text>{t("common.analyzedImages", "Analyzed {{count}} images", { count: imageCount })}</Text>
    </HStack>
  )
}
