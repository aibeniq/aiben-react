import { Heading, Stack, VStack } from "@chakra-ui/react"
import { useTheme } from "next-themes"
import { useTranslation } from "react-i18next"
import { Radio, RadioGroup } from "../ui/radio"

const Appearance = () => {
  const { theme, setTheme } = useTheme()
  const { t } = useTranslation()

  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm" color="fg">
        {t("settings.appearance")}
      </Heading>

      <RadioGroup
        onValueChange={(details) => setTheme(details.value || "system")}
        value={theme || "system"}
        colorPalette="teal"
      >
        <Stack>
          <Radio value="system" color="fg">
            {t("settings.system")}
          </Radio>
          <Radio value="light" color="fg">
            {t("settings.lightMode")}
          </Radio>
          <Radio value="dark" color="fg">
            {t("settings.darkMode")}
          </Radio>
        </Stack>
      </RadioGroup>
    </VStack>
  )
}

export default Appearance
