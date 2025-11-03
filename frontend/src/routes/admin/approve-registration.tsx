import { Alert, Container, Spinner, Text } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useSearch } from "@tanstack/react-router"

import { UsersService } from "@/client"

export const Route = createFileRoute("/admin/approve-registration")({
  component: ApproveRegistration,
  validateSearch: (search: { token?: string }) => ({
    token: search.token || "",
  }),
})

function ApproveRegistration() {
  const { token } = useSearch({ from: "/admin/approve-registration" })

  const { data, isLoading, error, isSuccess } = useQuery({
    queryKey: ["approve-registration", token],
    queryFn: () => UsersService.approveRegistration({ token }),
    enabled: !!token,
    retry: false,
  })

  if (isLoading) {
    return (
      <Container centerContent maxW="md" py={12}>
        <Spinner size="xl" />
        <Text mt={4}>Processing approval...</Text>
      </Container>
    )
  }

  if (error) {
    return (
      <Container centerContent maxW="md" py={12}>
        <Alert.Root status="error">
          <Alert.Indicator />
          <Alert.Title>Approval Failed</Alert.Title>
          <Alert.Description>
            Invalid or expired approval link. The token may have expired or
            already been used.
          </Alert.Description>
        </Alert.Root>
      </Container>
    )
  }

  if (isSuccess) {
    return (
      <Container centerContent maxW="md" py={12}>
        <Alert.Root status="success">
          <Alert.Indicator />
          <Alert.Title>Registration Approved</Alert.Title>
          <Alert.Description>
            {data.message ||
              "The user registration has been successfully approved."}
            <br />
            The user will receive a welcome email shortly.
          </Alert.Description>
        </Alert.Root>
      </Container>
    )
  }

  return null
}
