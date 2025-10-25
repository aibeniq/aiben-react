import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useSearch } from "@tanstack/react-router"
import { Container, Text, Spinner, Alert } from "@chakra-ui/react"

import { UsersService } from "@/client"

export const Route = createFileRoute("/admin/reject-registration")({
  component: RejectRegistration,
  validateSearch: (search: { token?: string }) => ({
    token: search.token || "",
  }),
})

function RejectRegistration() {
  const { token } = useSearch({ from: "/admin/reject-registration" })

  const { data, isLoading, error, isSuccess } = useQuery({
    queryKey: ["reject-registration", token],
    queryFn: () => UsersService.rejectRegistration({ token }),
    enabled: !!token,
    retry: false,
  })

  if (isLoading) {
    return (
      <Container centerContent maxW="md" py={12}>
        <Spinner size="xl" />
        <Text mt={4}>Processing rejection...</Text>
      </Container>
    )
  }

  if (error) {
    return (
      <Container centerContent maxW="md" py={12}>
        <Alert.Root status="error">
          <Alert.Indicator />
          <Alert.Title>Rejection Failed</Alert.Title>
          <Alert.Description>
            Invalid or expired rejection link. The token may have expired or already been used.
          </Alert.Description>
        </Alert.Root>
      </Container>
    )
  }

  if (isSuccess) {
    return (
      <Container centerContent maxW="md" py={12}>
        <Alert.Root status="warning">
          <Alert.Indicator />
          <Alert.Title>Registration Rejected</Alert.Title>
          <Alert.Description>
            {data.message ||
              "The user registration has been rejected and the account has been removed."}
          </Alert.Description>
        </Alert.Root>
      </Container>
    )
  }

  return null
}
