import HelpTooltip from "@/components/ui/help-tooltip"
import { Tooltip } from "@/components/ui/tooltip"
import {
  Badge,
  Box,
  Container,
  EmptyState,
  Flex,
  HStack,
  Heading,
  Table,
  Text,
  VStack,
} from "@chakra-ui/react"
import { Switch } from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { FiChevronDown, FiChevronUp, FiSearch } from "react-icons/fi"
import { z } from "zod"

import { KnowledgeBaseActionsMenu } from "@/components/Common/KnowledgeBaseActionsMenu"
import AddKnowledgeBase from "@/components/KnowledgeBases/AddKnowledgeBase"
import PendingKnowledgeBases from "@/components/Pending/PendingKnowledgeBases"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"
import { useKnowledgeBases } from "@/hooks/useKnowledgeBases"

const knowledgeBasesSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

export const Route = createFileRoute("/_layout/knowledge-bases")({
  component: KnowledgeBases,
  validateSearch: (search) => knowledgeBasesSearchSchema.parse(search),
})

function KnowledgeBasesTable() {
  const { t } = useTranslation()
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()
  const { knowledgeBases, isLoading, showAllUsers, toggleShowAllUsers, canViewAllUsers } =
    useKnowledgeBases()

  // Add sorting state
  const [sortBy, setSortBy] = useState<string | null>(null)
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc")

  // Sorting function
  const sortKnowledgeBases = (kbs: any[]) => {
    if (!sortBy) return kbs
    return [...kbs].sort((a, b) => {
      let aVal: any
      let bVal: any
      switch (sortBy) {
        case "title":
          aVal = (a.title || "").toLowerCase()
          bVal = (b.title || "").toLowerCase()
          break
        case "description":
          aVal = (a.description || "").toLowerCase()
          bVal = (b.description || "").toLowerCase()
          break
        case "number_of_sources":
          aVal = a.number_of_sources || 0
          bVal = b.number_of_sources || 0
          break
        case "total_pages":
          aVal = a.total_pages || 0
          bVal = b.total_pages || 0
          break
        case "embedding_model_name":
          aVal = (a.embedding_model_name || "").toLowerCase()
          bVal = (b.embedding_model_name || "").toLowerCase()
          break
        case "date_created":
          aVal = new Date(a.date_created).getTime()
          bVal = new Date(b.date_created).getTime()
          break
        case "date_modified":
          aVal = new Date(a.date_modified).getTime()
          bVal = new Date(b.date_modified).getTime()
          break
        default:
          return 0
      }
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1
      return 0
    })
  }

  // Handle sort click
  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc")
    } else {
      setSortBy(column)
      setSortOrder("asc")
    }
    // Reset to first page when sorting changes
    setPage(1)
  }

  // Sort the knowledge bases before pagination
  const sortedKnowledgeBases = sortKnowledgeBases(knowledgeBases)
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const startIndex = (page - 1) * PER_PAGE
  const endIndex = startIndex + PER_PAGE
  const items = sortedKnowledgeBases.slice(startIndex, endIndex)
  const count = sortedKnowledgeBases.length
  const isPlaceholderData = false

  if (isLoading) {
    return (
      <>
        {/* All Users Toggle - Only visible to superusers */}
        {canViewAllUsers && (
          <HStack justifyContent="flex-end" mb={4}>
            <Tooltip
              content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
            >
              <HStack gap={2}>
                <HStack gap={1} align="center">
                  <Text fontSize="xs" color="gray.500">
                    {t("archive.allUsers")}
                  </Text>
                  <HelpTooltip helpKey="allUsersToggle" />
                </HStack>
                <Switch.Root
                  key={`switch-${showAllUsers}`}
                  size="sm"
                  colorPalette="blue"
                  checked={showAllUsers}
                >
                  <Switch.HiddenInput
                    checked={showAllUsers}
                    onChange={() => {
                      console.log(
                        "Knowledge Bases toggle clicked, current showAllUsers:",
                        showAllUsers,
                      )
                      if (toggleShowAllUsers) toggleShowAllUsers()
                    }}
                  />
                  <Switch.Control data-state={showAllUsers ? "checked" : "unchecked"}>
                    <Switch.Thumb />
                  </Switch.Control>
                </Switch.Root>
              </HStack>
            </Tooltip>
          </HStack>
        )}
        <PendingKnowledgeBases />
      </>
    )
  }

  if (knowledgeBases.length === 0) {
    return (
      <>
        {/* All Users Toggle - Only visible to superusers */}
        {canViewAllUsers && (
          <HStack justifyContent="flex-end" mb={4}>
            <Tooltip
              content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
            >
              <HStack gap={2}>
                <HStack gap={1} align="center">
                  <Text fontSize="xs" color="gray.500">
                    {t("archive.allUsers")}
                  </Text>
                  <HelpTooltip helpKey="allUsersToggle" />
                </HStack>
                <Switch.Root
                  key={`switch-${showAllUsers}`}
                  size="sm"
                  colorPalette="blue"
                  checked={showAllUsers}
                >
                  <Switch.HiddenInput
                    checked={showAllUsers}
                    onChange={() => {
                      console.log(
                        "Knowledge Bases toggle clicked, current showAllUsers:",
                        showAllUsers,
                      )
                      if (toggleShowAllUsers) toggleShowAllUsers()
                    }}
                  />
                  <Switch.Control data-state={showAllUsers ? "checked" : "unchecked"}>
                    <Switch.Thumb />
                  </Switch.Control>
                </Switch.Root>
              </HStack>
            </Tooltip>
          </HStack>
        )}
        <EmptyState.Root>
          <EmptyState.Content>
            <EmptyState.Indicator>
              <FiSearch />
            </EmptyState.Indicator>
            <VStack textAlign="center">
              <EmptyState.Title>{t("knowledgeBases.emptyStateTitle")}</EmptyState.Title>
              <EmptyState.Description>
                {t("knowledgeBases.emptyStateDescription")}
              </EmptyState.Description>
            </VStack>
          </EmptyState.Content>
        </EmptyState.Root>
      </>
    )
  }

  return (
    <>
      {/* All Users Toggle - Only visible to superusers */}
      {canViewAllUsers && (
        <HStack justifyContent="flex-end" mb={4}>
          <Tooltip
            content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
          >
            <HStack gap={2}>
              <HStack gap={1} align="center">
                <Text fontSize="xs" color="gray.500">
                  {t("archive.allUsers")}
                </Text>
                <HelpTooltip helpKey="allUsersToggle" />
              </HStack>
              <Switch.Root
                key={`switch-${showAllUsers}`}
                size="sm"
                colorPalette="blue"
                checked={showAllUsers}
              >
                <Switch.HiddenInput
                  checked={showAllUsers}
                  onChange={() => {
                    console.log(
                      "Knowledge Bases toggle clicked, current showAllUsers:",
                      showAllUsers,
                    )
                    if (toggleShowAllUsers) toggleShowAllUsers()
                  }}
                />
                <Switch.Control data-state={showAllUsers ? "checked" : "unchecked"}>
                  <Switch.Thumb />
                </Switch.Control>
              </Switch.Root>
            </HStack>
          </Tooltip>
        </HStack>
      )}

      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm" cursor="pointer" onClick={() => handleSort("title")}>
              {t("knowledgeBases.tableHeaders.title")}
              {sortBy === "title" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader w="sm" cursor="pointer" onClick={() => handleSort("description")}>
              {t("knowledgeBases.tableHeaders.description")}
              {sortBy === "description" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader
              w="sm"
              cursor="pointer"
              onClick={() => handleSort("number_of_sources")}
            >
              {t("knowledgeBases.tableHeaders.numberOfSources")}
              {sortBy === "number_of_sources" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader w="sm" cursor="pointer" onClick={() => handleSort("total_pages")}>
              {t("chatbot.knowledgeBaseTablePages")}
              {sortBy === "total_pages" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader
              w="sm"
              cursor="pointer"
              onClick={() => handleSort("embedding_model_name")}
            >
              {t("knowledgeBases.tableHeaders.embeddingModel")}
              {sortBy === "embedding_model_name" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader w="sm" cursor="pointer" onClick={() => handleSort("date_created")}>
              {t("knowledgeBases.tableHeaders.dateCreated")}
              {sortBy === "date_created" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader w="sm" cursor="pointer" onClick={() => handleSort("date_modified")}>
              {t("knowledgeBases.tableHeaders.dateModified")}
              {sortBy === "date_modified" &&
                (sortOrder === "asc" ? (
                  <FiChevronUp style={{ display: "inline", marginLeft: "4px" }} />
                ) : (
                  <FiChevronDown style={{ display: "inline", marginLeft: "4px" }} />
                ))}
            </Table.ColumnHeader>
            <Table.ColumnHeader w="sm">
              {t("knowledgeBases.tableHeaders.actions")}
            </Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {items?.map((item) => (
            <Table.Row key={item.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {item.title}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.description || t("knowledgeBases.status.na")}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.number_of_sources}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.total_pages || 0}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.embedding_model_name ? (
                  <Badge colorPalette="blue" size="sm">
                    {item.embedding_model_name}
                  </Badge>
                ) : (
                  <Badge colorPalette="gray" size="sm">
                    {t("knowledgeBases.status.default")}
                  </Badge>
                )}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {new Date(item.date_created).toLocaleDateString()}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {new Date(item.date_modified).toLocaleDateString()}
              </Table.Cell>
              <Table.Cell>
                <KnowledgeBaseActionsMenu item={item} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      {count > PER_PAGE && (
        <Flex justifyContent="flex-end" mt={4}>
          <PaginationRoot
            count={count}
            pageSize={PER_PAGE}
            onPageChange={({ page }) => setPage(page)}
          >
            <Flex>
              <PaginationPrevTrigger />
              <PaginationItems />
              <PaginationNextTrigger />
            </Flex>
          </PaginationRoot>
        </Flex>
      )}
    </>
  )
}

function KnowledgeBases() {
  const { t } = useTranslation()
  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>
            {t("knowledgeBases.title")}
          </Heading>
          <AddKnowledgeBase />
        </Box>
        <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={4} bg="bg">
          <KnowledgeBasesTable />
        </Box>
      </VStack>
    </Container>
  )
}
