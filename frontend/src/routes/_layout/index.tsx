import {
  Box,
  Container,
  Text,
  Card,
  VStack,
  HStack,
  Progress,
  Skeleton,
  Alert,
  IconButton,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { HiRefresh } from "react-icons/hi"
import { UsageService } from "@/client"

import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function UsageStats() {
  const {
    data: usageData,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ["usage", "token-usage"],
    queryFn: () => UsageService.getTokenUsage(),
    refetchInterval: 5 * 60 * 1000, // refetch every 5 minutes
  })

  const handleRefresh = () => {
    refetch()
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  if (error) {
    return (
      <Alert.Root status="error">
        <Alert.Indicator />
        <Alert.Title>Unable to load usage data</Alert.Title>
      </Alert.Root>
    )
  }

  const totalTokens = usageData?.total_tokens || 0
  const quotaPeriod = usageData?.quota_period
  const maxTokens = quotaPeriod?.max_tokens || 50_000_000
  const percentage = Math.min((totalTokens / maxTokens) * 100, 100)

  const startDate = quotaPeriod?.start_date ? new Date(quotaPeriod.start_date) : null
  const endDate = quotaPeriod?.end_date ? new Date(quotaPeriod.end_date) : null

  return (
    <VStack align="stretch" gap={6}>
      <HStack justify="space-between" align="center">
        <Box>
          <Text fontSize="xl" fontWeight="semibold" mb={2}>
            Usage
          </Text>
          <VStack align="start" gap={1}>
            <Text fontSize="sm" color="gray.500">
              Current period:{" "}
              {startDate && endDate
                ? `${formatDate(startDate)} - ${formatDate(endDate)}`
                : "Loading..."}
            </Text>
          </VStack>
        </Box>
      </HStack>

      <Card.Root>
        <Card.Body p={8}>
          {isLoading ? (
            <VStack align="stretch" gap={4}>
              <Skeleton height="6" />
              <Skeleton height="4" width="100px" mx="auto" />
            </VStack>
          ) : (
            <VStack align="stretch" gap={6}>
              <VStack align="stretch" gap={4}>
                <HStack justify="space-between" align="center">
                  <HStack align="center" gap={1}>
                    <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                      {percentage.toFixed(1)}%
                    </Text>
                    <Text fontSize="sm" color="gray.500">
                      used of your monthly quota
                    </Text>
                  </HStack>
                  <IconButton
                    aria-label="Refresh usage data"
                    size="sm"
                    variant="ghost"
                    onClick={handleRefresh}
                    disabled={isFetching}
                  >
                    <HiRefresh />
                  </IconButton>
                </HStack>
                <Progress.Root value={percentage} size="lg" colorPalette="blue">
                  <Progress.Track>
                    <Progress.Range />
                  </Progress.Track>
                </Progress.Root>
              </VStack>
            </VStack>
          )}
        </Card.Body>
      </Card.Root>
    </VStack>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl" truncate maxW="sm">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text mb={8}>Welcome back, nice to see you again!</Text>

          <UsageStats />
        </Box>
      </Container>
    </>
  )
}
