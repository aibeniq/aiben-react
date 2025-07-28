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
  const calculateQuotaPeriod = () => {
    const today = new Date()
    const currentDay = today.getDate()
    const currentMonth = today.getMonth()
    const currentYear = today.getFullYear()

    let startDate: Date
    let endDate: Date

    if (currentDay >= 28) {
      // current quota period: this month's 28th to next month's 27th
      startDate = new Date(currentYear, currentMonth, 28)
      endDate = new Date(currentYear, currentMonth + 1, 27, 23, 59, 59) // end of 27th
    } else {
      // current quota period: last month's 28th to this month's 27th
      startDate = new Date(currentYear, currentMonth - 1, 28)
      endDate = new Date(currentYear, currentMonth, 27, 23, 59, 59) // end of 27th
    }

    return {
      startTime: Math.floor(startDate.getTime() / 1000),
      endTime: Math.floor(endDate.getTime() / 1000),
      startDate,
      endDate,
    }
  }

  const { startTime, endTime, startDate, endDate } = calculateQuotaPeriod()

  const {
    data: usageData,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ["usage", "token-usage", startTime, endTime],
    queryFn: () =>
      UsageService.getTokenUsage({
        startTime,
        endTime,
      }),
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

  const totalTokens = (usageData as any)?.total_tokens || 0
  const maxTokens = 50_000_000
  const percentage = Math.min((totalTokens / maxTokens) * 100, 100)

  return (
    <VStack align="stretch" gap={6}>
      <HStack justify="space-between" align="center">
        <Box>
          <Text fontSize="xl" fontWeight="semibold" mb={2}>
            Usage
          </Text>
          <VStack align="start" gap={1}>
            <Text fontSize="sm" color="gray.500">
              Current period: {formatDate(startDate)} - {formatDate(endDate)}
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
