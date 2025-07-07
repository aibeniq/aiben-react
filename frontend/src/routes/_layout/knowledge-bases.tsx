import { Container, EmptyState, Flex, Heading, Table, VStack, Badge, Box } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { KnowledgeBasesService } from "@/client"
import { KnowledgeBaseActionsMenu } from "@/components/Common/KnowledgeBaseActionsMenu"
import AddKnowledgeBase from "@/components/KnowledgeBases/AddKnowledgeBase"
import PendingKnowledgeBases from "@/components/Pending/PendingKnowledgeBases"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const knowledgeBasesSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getKnowledgeBasesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      KnowledgeBasesService.readKnowledgeBases({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["items", { page }],
  }
}

export const Route = createFileRoute("/_layout/knowledge-bases")({
  component: KnowledgeBases,
  validateSearch: (search) => knowledgeBasesSearchSchema.parse(search),
})

function KnowledgeBasesTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getKnowledgeBasesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const items = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingKnowledgeBases />
  }

  if (items.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any Knowledge Bases yet</EmptyState.Title>
            <EmptyState.Description>Add a new Knowledge Base to get started</EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Number of Sources</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Embedding Model</Table.ColumnHeader> {/* Add this line */}
            <Table.ColumnHeader w="sm">Date Created</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Date Modified</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {items?.map((item) => (
            <Table.Row key={item.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {item.title}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.description || "N/A"}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.number_of_sources}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.embedding_model.model_name ? (
                  <Badge colorPalette="blue" size="sm">
                    {item.embedding_model.model_name}
                  </Badge>
                ) : (
                  <Badge colorPalette="gray" size="sm">
                    Default
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
    </>
  )
}

function KnowledgeBases() {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>
            Knowledge Base Management
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
