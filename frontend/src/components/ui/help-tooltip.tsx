import { Icon } from "@chakra-ui/react"
import type React from "react"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { FiHelpCircle } from "react-icons/fi"
import { Tooltip } from "./tooltip"

export interface HelpTooltipProps {
  /** The help key to look up in translations (e.g., "dashboard", "review") */
  helpKey: string
  /** Size of the help icon */
  size?: string | number
  /** Color of the help icon */
  color?: string
  /** Additional margin/spacing */
  ml?: string | number
  /** Additional props to pass to the icon */
  iconProps?: React.ComponentProps<typeof Icon>
  /** Custom tooltip content (overrides translation lookup) */
  content?: React.ReactNode
}

/**
 * HelpTooltip component that displays a question mark icon with localized help text
 * Uses the translation key "help.{helpKey}" and falls back to English if not found
 */
export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  helpKey,
  size = "14px",
  color = "gray.500",
  ml = 2,
  iconProps,
  content,
  ...rest
}) => {
  const { t } = useTranslation()

  // Get the help text with automatic language detection
  // Use useMemo to make it reactive to language changes
  const helpText = useMemo(() => {
    if (content) return content

    // Use t() directly which automatically uses current language
    const translatedText = t(`help.${helpKey}`)

    // If translation is missing (returns the key), try English fallback
    if (translatedText === `help.${helpKey}`) {
      return t(`help.${helpKey}`, { lng: "en" })
    }

    return translatedText
  }, [content, helpKey, t])

  return (
    <Tooltip content={helpText} showArrow portalled {...rest}>
      <Icon
        as={FiHelpCircle}
        w={size}
        h={size}
        color={color}
        ml={ml}
        cursor="help"
        _hover={{ color: "blue.500" }}
        transition="color 0.2s"
        {...iconProps}
      />
    </Tooltip>
  )
}

export default HelpTooltip
