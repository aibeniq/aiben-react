import { UsageService } from "@/client"
import {
  Alert,
  Box,
  Card,
  Container,
  HStack,
  IconButton,
  Progress,
  Skeleton,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"
import { HiRefresh } from "react-icons/hi"

import { HelpTooltip } from "@/components/ui/help-tooltip"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function UsageStats() {
  const { t } = useTranslation()
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

  const startDate = quotaPeriod?.start_date
    ? new Date(quotaPeriod.start_date)
    : null
  const endDate = quotaPeriod?.end_date ? new Date(quotaPeriod.end_date) : null

  return (
    <VStack align="stretch" gap={6}>
      <HStack justify="space-between" align="center">
        <Box>
          <HStack align="center" mb={2}>
            <Text fontSize="xl" fontWeight="semibold">
              {t("usage.title")}
            </Text>
            <HelpTooltip helpKey="usageStats" />
          </HStack>
          <VStack align="start" gap={1}>
            <Text fontSize="sm" color="gray.500">
              {t("usage.currentPeriod")}{" "}
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
                      {t("usage.usedOfQuota")}
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
  const { t } = useTranslation()

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl" truncate maxW="sm">
            {t("common.hiUser", {
              name: currentUser?.full_name || currentUser?.email,
            })}
          </Text>
          <Text mb={8}>{t("common.welcomeBack")}</Text>

          <UsageStats />
        </Box>
      </Container>
    </>
  )
}
