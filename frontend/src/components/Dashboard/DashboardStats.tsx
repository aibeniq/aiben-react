import {
  FormconnectService,
  ReportgenieService,
  TwincheckService,
  VeradocService,
} from "@/client"
import {
  Alert,
  Badge,
  Box,
  Card,
  HStack,
  Icon,
  SimpleGrid,
  Skeleton,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { FaBalanceScale } from "react-icons/fa"
import {
  FiCheckCircle,
  FiFilePlus,
  FiMessageSquare,
  FiUser,
  FiUsers,
} from "react-icons/fi"
import { TbPlugConnected } from "react-icons/tb"

interface StatCardProps {
  title: string
  value: number
  icon: React.ElementType
  color: string
  isLoading?: boolean
}

function StatCard({ title, value, icon, color, isLoading }: StatCardProps) {
  if (isLoading) {
    return (
      <Card.Root>
        <Card.Body p={6}>
          <VStack align="stretch" gap={3}>
            <Skeleton height="6" />
            <Skeleton height="8" />
          </VStack>
        </Card.Body>
      </Card.Root>
    )
  }

  return (
    <Card.Root>
      <Card.Body p={6}>
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <Text fontSize="sm" color="gray.500">
              {title}
            </Text>
            <Text fontSize="2xl" fontWeight="bold" color={color}>
              {value.toLocaleString()}
            </Text>
          </VStack>
          <Icon as={icon} boxSize={8} color={color} />
        </HStack>
      </Card.Body>
    </Card.Root>
  )
}

export default function DashboardStats() {
  const [showAllUsers, setShowAllUsers] = useState(false)

  // Fetch data from existing endpoints
  const {
    data: veradocData,
    isLoading: veradocLoading,
    error: veradocError,
  } = useQuery({
    queryKey: ["veradocHistory", showAllUsers],
    queryFn: () =>
      VeradocService.getVeradocHistory({
        limit: 1000, // Get all to count
        showAll: showAllUsers,
      }),
    refetchInterval: 5 * 60 * 1000,
  })

  const {
    data: reportgenieData,
    isLoading: reportgenieLoading,
    error: reportgenieError,
  } = useQuery({
    queryKey: ["reportgenieHistory", showAllUsers],
    queryFn: () =>
      ReportgenieService.getReportgenieHistory({
        limit: 1000,
        showAll: showAllUsers,
      }),
    refetchInterval: 5 * 60 * 1000,
  })

  const {
    data: twincheckData,
    isLoading: twincheckLoading,
    error: twincheckError,
  } = useQuery({
    queryKey: ["twincheckHistory", showAllUsers],
    queryFn: () =>
      TwincheckService.getComparisonHistory({
        limit: 1000,
        showAll: showAllUsers,
      }),
    refetchInterval: 5 * 60 * 1000,
  })

  const {
    data: formconnectData,
    isLoading: formconnectLoading,
    error: formconnectError,
  } = useQuery({
    queryKey: ["formconnectHistory", showAllUsers],
    queryFn: () =>
      FormconnectService.getFormHistory({
        limit: 1000,
        showAll: showAllUsers,
      }),
    refetchInterval: 5 * 60 * 1000,
  })

  const isLoading =
    veradocLoading ||
    reportgenieLoading ||
    twincheckLoading ||
    formconnectLoading
  const hasError =
    veradocError || reportgenieError || twincheckError || formconnectError

  if (hasError) {
    return (
      <Alert.Root status="error">
        <Alert.Indicator />
        <Alert.Title>Unable to load dashboard statistics</Alert.Title>
      </Alert.Root>
    )
  }

  const stats = {
    reviews: Array.isArray(veradocData) ? veradocData.length : 0,
    generated_documents: Array.isArray(reportgenieData)
      ? reportgenieData.length
      : 0,
    document_comparisons: Array.isArray(twincheckData)
      ? twincheckData.length
      : 0,
    matched_document_sets: Array.isArray(formconnectData)
      ? formconnectData.length
      : 0,
    chat_completions: 0, // TODO: Add chat history endpoint
  }

  return (
    <VStack align="stretch" gap={6}>
      <HStack justify="space-between" align="center">
        <Box>
          <Text fontSize="xl" fontWeight="semibold" mb={2}>
            Activity Statistics
          </Text>
          <Text fontSize="sm" color="gray.500">
            Track your AI-powered document processing activities
          </Text>
        </Box>
        <HStack align="center" gap={3}>
          <Icon as={showAllUsers ? FiUsers : FiUser} />
          <Text fontSize="sm" color="gray.600">
            {showAllUsers ? "All Users" : "Your Activity"}
          </Text>
          <label>
            <input
              type="checkbox"
              checked={showAllUsers}
              onChange={(e) => setShowAllUsers(e.target.checked)}
              style={{ marginLeft: "8px" }}
            />
          </label>
        </HStack>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 5 }} gap={4}>
        <StatCard
          title="Document Reviews"
          value={stats.reviews}
          icon={FiCheckCircle}
          color="green.500"
          isLoading={isLoading}
        />
        <StatCard
          title="Generated Reports"
          value={stats.generated_documents}
          icon={FiFilePlus}
          color="blue.500"
          isLoading={isLoading}
        />
        <StatCard
          title="Document Comparisons"
          value={stats.document_comparisons}
          icon={FaBalanceScale}
          color="purple.500"
          isLoading={isLoading}
        />
        <StatCard
          title="Form Matches"
          value={stats.matched_document_sets}
          icon={TbPlugConnected}
          color="orange.500"
          isLoading={isLoading}
        />
        <StatCard
          title="Chat Sessions"
          value={stats.chat_completions}
          icon={FiMessageSquare}
          color="teal.500"
          isLoading={isLoading}
        />
      </SimpleGrid>

      {showAllUsers && (
        <Box mt={2}>
          <Badge variant="subtle" colorPalette="blue">
            Platform-wide statistics across all users
          </Badge>
        </Box>
      )}
    </VStack>
  )
}
