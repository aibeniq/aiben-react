import { Heading, Text, VStack } from "@chakra-ui/react"
import { useTranslation } from "react-i18next"

import DeleteConfirmation from "./DeleteConfirmation"

const DeleteAccount = () => {
  const { t } = useTranslation()

  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm">{t("settings.deleteAccount")}</Heading>
      <Text>{t("settings.deleteAccountDescription")}</Text>
      <DeleteConfirmation />
    </VStack>
  )
}
export default DeleteAccount
