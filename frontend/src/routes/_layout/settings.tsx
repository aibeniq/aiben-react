import { Box, Container, Heading, Tabs, VStack } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import Appearance from "@/components/UserSettings/Appearance"
import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import LanguageSettings from "@/components/UserSettings/LanguageSettings"
import ProcessingDefaultsSettings from "@/components/UserSettings/ProcessingDefaultsSettings"
import UserInformation from "@/components/UserSettings/UserInformation"
import useAuth from "@/hooks/useAuth"

const tabsConfig = [
  {
    value: "my-profile",
    title: "My profile",
    titleKey: "navigation.myProfile",
    component: UserInformation,
  },
  {
    value: "language",
    title: "Language",
    titleKey: "settings.language",
    component: LanguageSettings,
  },
  {
    value: "processing-defaults",
    title: "Processing Defaults",
    titleKey: "settings.processingDefaults.tab",
    component: ProcessingDefaultsSettings,
  },
  {
    value: "password",
    title: "Password",
    titleKey: "settings.changePassword",
    component: ChangePassword,
  },
  {
    value: "appearance",
    title: "Appearance",
    titleKey: "settings.appearance",
    component: Appearance,
  },
  {
    value: "danger-zone",
    title: "Danger zone",
    titleKey: "settings.dangerZone",
    component: DeleteAccount,
  },
]

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
})

function UserSettings() {
  const { user: currentUser } = useAuth()
  const { t } = useTranslation()
  const finalTabs = currentUser?.is_superuser ? tabsConfig.slice(0, 3) : tabsConfig

  if (!currentUser) {
    return null
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>
            {t("settings.title")}
          </Heading>
        </Box>
        <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={4} bg="bg">
          <Tabs.Root defaultValue="my-profile" variant="subtle">
            <Tabs.List>
              {finalTabs.map((tab) => (
                <Tabs.Trigger key={tab.value} value={tab.value}>
                  {tab.titleKey ? t(tab.titleKey) : tab.title}
                </Tabs.Trigger>
              ))}
            </Tabs.List>
            {finalTabs.map((tab) => (
              <Tabs.Content key={tab.value} value={tab.value}>
                <tab.component />
              </Tabs.Content>
            ))}
          </Tabs.Root>
        </Box>
      </VStack>
    </Container>
  )
}
