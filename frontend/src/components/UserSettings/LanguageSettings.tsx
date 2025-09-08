import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { useLanguage } from "@/hooks/useLanguage"
import { Box, Card, VStack } from "@chakra-ui/react"
import React from "react"

const LanguageSettings: React.FC = () => {
  const { currentLanguage, availableLanguages, changeLanguage, isUpdating, t } =
    useLanguage()
  const [selectedLanguage, setSelectedLanguage] =
    React.useState(currentLanguage)

  const handleSave = () => {
    changeLanguage(selectedLanguage)
  }

  const handleLanguageChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ) => {
    setSelectedLanguage(event.target.value)
  }

  return (
    <Card.Root p={4}>
      <Card.Body>
        <VStack gap={6} align="stretch">
          <Field label={t("settings.preferredLanguage")}>
            <select
              value={selectedLanguage}
              onChange={handleLanguageChange}
              className="chakra-select"
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "0.375rem",
                border: "1px solid",
                borderColor: "inherit",
              }}
            >
              {Object.entries(availableLanguages).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
          </Field>

          <Box>
            <Button
              colorPalette="blue"
              loading={isUpdating}
              onClick={handleSave}
              disabled={selectedLanguage === currentLanguage}
            >
              {t("settings.saveLanguagePreference")}
            </Button>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default LanguageSettings
