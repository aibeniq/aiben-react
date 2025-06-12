import { Container, Heading, Tabs, VStack, Box } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import Appearance from "@/components/UserSettings/Appearance"
import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import UserInformation from "@/components/UserSettings/UserInformation"
import useAuth from "@/hooks/useAuth"

const tabsConfig = [
  { value: "my-profile", title: "My profile", component: UserInformation },
  { value: "password", title: "Password", component: ChangePassword },
  { value: "appearance", title: "Appearance", component: Appearance },
  { value: "danger-zone", title: "Danger zone", component: DeleteAccount },
]

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
})

function UserSettings() {
  const { user: currentUser } = useAuth()
  const finalTabs = currentUser?.is_superuser ? tabsConfig.slice(0, 3) : tabsConfig

  if (!currentUser) {
    return null
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>
            User Settings
          </Heading>
        </Box>
        <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={4} bg="bg">
          <Tabs.Root defaultValue="my-profile" variant="subtle">
            <Tabs.List>
              {finalTabs.map((tab) => (
                <Tabs.Trigger key={tab.value} value={tab.value}>
                  {tab.title}
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
