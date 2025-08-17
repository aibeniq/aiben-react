import {
  Box,
  Text,
  Card,
  VStack,
  HStack,
  Icon,
  Badge,
  Skeleton,
  Alert,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { VeradocService, ReportgenieService, TwincheckService, FormconnectService } from "@/client"
import { 
  FiCheckCircle, 
  FiFilePlus, 
  FiClock,
  FiUser,
  FiCalendar
} from "react-icons/fi"
import { FaBalanceScale } from "react-icons/fa"
import { TbPlugConnected } from "react-icons/tb"

interface ActivityItem {
  id: string
  type: "veradoc" | "reportgenie" | "twincheck" | "formconnect"
  title: string
  timestamp: string
  user_email?: string
}

interface ActivityItemProps {
  activity: ActivityItem
}

const typeConfig = {
  veradoc: {
    icon: FiCheckCircle,
    color: "green.500",
    label: "Document Review",
    bgColor: "green.50",
  },
  reportgenie: {
    icon: FiFilePlus,
    color: "blue.500",
    label: "Report Generated",
    bgColor: "blue.50",
  },
  twincheck: {
    icon: FaBalanceScale,
    color: "purple.500",
    label: "Document Comparison",
    bgColor: "purple.50",
  },
  formconnect: {
    icon: TbPlugConnected,
    color: "orange.500",
    label: "Form Match",
    bgColor: "orange.50",
  },
}

function ActivityItemCard({ activity }: ActivityItemProps) {
  const config = typeConfig[activity.type]
  const date = new Date(activity.timestamp)
  
  return (
    <Card.Root size="sm" bg={config.bgColor}>
      <Card.Body p={4}>
        <HStack align="start" gap={3}>
          <Box
            p={2}
            borderRadius="md"
            bg="white"
            border="1px solid"
            borderColor="gray.200"
          >
            <Icon as={config.icon} color={config.color} boxSize={4} />
          </Box>
          <VStack align="start" gap={1} flex={1}>
            <HStack align="center" gap={2}>
              <Badge variant="subtle" colorPalette={config.color.split('.')[0]}>
                {config.label}
              </Badge>
              <HStack align="center" gap={1}>
                <Icon as={FiClock} boxSize={3} color="gray.400" />
                <Text fontSize="xs" color="gray.500">
                  {date.toLocaleDateString()} {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </HStack>
            </HStack>
            <Text fontSize="sm" fontWeight="medium" color="gray.700">
              {activity.title}
            </Text>
            {activity.user_email && (
              <HStack align="center" gap={1}>
                <Icon as={FiUser} boxSize={3} color="gray.400" />
                <Text fontSize="xs" color="gray.500">
                  {activity.user_email}
                </Text>
              </HStack>
            )}
          </VStack>
        </HStack>
      </Card.Body>
    </Card.Root>
  )
}

export default function RecentActivity() {
  // Fetch recent data from each service
  const {
    data: veradocData,
    isLoading: veradocLoading,
    error: veradocError,
  } = useQuery({
    queryKey: ["veradocRecent"],
    queryFn: () => VeradocService.getVeradocHistory({
      limit: 5,
      showAll: true
    }),
    refetchInterval: 2 * 60 * 1000, // refetch every 2 minutes
  })

  const {
    data: reportgenieData,
    isLoading: reportgenieLoading,
    error: reportgenieError,
  } = useQuery({
    queryKey: ["reportgenieRecent"],
    queryFn: () => ReportgenieService.getReportgenieHistory({
      limit: 5,
      showAll: true
    }),
    refetchInterval: 2 * 60 * 1000,
  })

  const {
    data: twincheckData,
    isLoading: twincheckLoading,
    error: twincheckError,
  } = useQuery({
    queryKey: ["twincheckRecent"],
    queryFn: () => TwincheckService.getComparisonHistory({
      limit: 5,
      showAll: true
    }),
    refetchInterval: 2 * 60 * 1000,
  })

  const {
    data: formconnectData,
    isLoading: formconnectLoading,
    error: formconnectError,
  } = useQuery({
    queryKey: ["formconnectRecent"],
    queryFn: () => FormconnectService.getFormHistory({
      limit: 5,
      showAll: true
    }),
    refetchInterval: 2 * 60 * 1000,
  })

  const isLoading = veradocLoading || reportgenieLoading || twincheckLoading || formconnectLoading
  const hasError = veradocError || reportgenieError || twincheckError || formconnectError

  if (hasError) {
    return (
      <Alert.Root status="error">
        <Alert.Indicator />
        <Alert.Title>Unable to load recent activity</Alert.Title>
      </Alert.Root>
    )
  }

  // Combine and sort all activities
  const allActivities: ActivityItem[] = []

  if (Array.isArray(veradocData)) {
    veradocData.forEach((item: any) => {
      allActivities.push({
        id: `veradoc-${item.id}`,
        type: "veradoc",
        title: item.filename || "Document Review",
        timestamp: item.created_at || item.timestamp,
        user_email: item.user_email,
      })
    })
  }

  if (Array.isArray(reportgenieData)) {
    reportgenieData.forEach((item: any) => {
      allActivities.push({
        id: `reportgenie-${item.id}`,
        type: "reportgenie",
        title: item.filename || "Report Generated",
        timestamp: item.created_at || item.timestamp,
        user_email: item.user_email,
      })
    })
  }

  if (Array.isArray(twincheckData)) {
    twincheckData.forEach((item: any) => {
      allActivities.push({
        id: `twincheck-${item.id}`,
        type: "twincheck",
        title: `${item.filename1 || 'Document'} vs ${item.filename2 || 'Document'}`,
        timestamp: item.created_at || item.timestamp,
        user_email: item.user_email,
      })
    })
  }

  if (Array.isArray(formconnectData)) {
    formconnectData.forEach((item: any) => {
      allActivities.push({
        id: `formconnect-${item.id}`,
        type: "formconnect",
        title: item.filename || "Form Processing",
        timestamp: item.created_at || item.timestamp,
        user_email: item.user_email,
      })
    })
  }

  // Sort by timestamp (most recent first) and take top 5
  const recentActivities = allActivities
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 5)

  if (isLoading) {
    return (
      <VStack align="stretch" gap={4}>
        <Box>
          <Text fontSize="xl" fontWeight="semibold" mb={2}>
            Recent Activity
          </Text>
          <Text fontSize="sm" color="gray.500">
            Latest AI operations across all tools
          </Text>
        </Box>
        <VStack align="stretch" gap={3}>
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} height="20" />
          ))}
        </VStack>
      </VStack>
    )
  }

  return (
    <VStack align="stretch" gap={4}>
      <Box>
        <Text fontSize="xl" fontWeight="semibold" mb={2}>
          Recent Activity
        </Text>
        <Text fontSize="sm" color="gray.500">
          Latest AI operations across all tools
        </Text>
      </Box>
      
      {recentActivities.length === 0 ? (
        <Card.Root>
          <Card.Body p={6} textAlign="center">
            <Icon as={FiCalendar} boxSize={8} color="gray.300" mb={2} />
            <Text color="gray.500">No recent activity found</Text>
          </Card.Body>
        </Card.Root>
      ) : (
        <VStack align="stretch" gap={3}>
          {recentActivities.map((activity) => (
            <ActivityItemCard key={activity.id} activity={activity} />
          ))}
        </VStack>
      )}
    </VStack>
  )
}
