import { Heading, Text, VStack } from "@chakra-ui/react"

import DeleteConfirmation from "./DeleteConfirmation"

const DeleteAccount = () => {
  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm">Delete Account</Heading>
      <Text>
        Permanently delete your data and everything associated with your
        account.
      </Text>
      <DeleteConfirmation />
    </VStack>
  )
}
export default DeleteAccount
