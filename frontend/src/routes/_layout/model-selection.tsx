import {
  Box,
  Button,
  Container,
  EmptyState,
  Flex,
  Heading,
  HStack,
  Spinner,
  Table,
  Badge,
  VStack,
  Separator,
  Show,
  Icon,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState, useEffect } from "react"
import { FiPlus, FiSettings } from "react-icons/fi"
import useCustomToast from "@/hooks/useCustomToast"
import { AiOutlineAmazon, AiOutlineOpenAI } from "react-icons/ai"
import { SiHuggingface, SiOllama } from "react-icons/si"

// This will need to be added to your SDK client
import { LlmModelsService, EmbeddingModelsService } from "@/client"

export const Route = createFileRoute("/_layout/model-selection")({
  component: ModelSelection,
})

const getProviderDisplayName = (provider: string) => {
  switch (provider) {
    case "huggingface":
      return (
        <HStack gap={1}>
          <Icon as={SiHuggingface} />
          HuggingFace
        </HStack>
      )
    case "openai":
      return (
        <HStack gap={1}>
          <Icon as={AiOutlineOpenAI} />
          OpenAI
        </HStack>
      )
    case "ollama":
      return (
        <HStack gap={1}>
          <Icon as={SiOllama} />
          Ollama
        </HStack>
      )
    case "replicate":
      return "Replicate"
    case "aws":
      return (
        <HStack gap={1}>
          <Icon as={AiOutlineAmazon} />
          Bedrock
        </HStack>
      )
    default:
      return provider
  }
}

const getProviderColor = (provider: string) => {
  switch (provider) {
    case "huggingface":
      return "teal"
    case "openai":
      return "blue"
    case "ollama":
      return "purple"
    case "replicate":
      return "red"
    case "aws":
      return "orange"
    default:
      return "gray"
  }
}

function ModelSelection() {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* First section: Embedding Models */}
        <Box>
          <EmbeddingModels />
        </Box>
        {/* Divider between sections */}
        <Separator my={4} />
        {/* Second section: LLMs */}
        <Box>
          <LlmModels />
        </Box>
      </VStack>
    </Container>
  )
}

function LlmModels() {
  // Similar to your EmbeddingModels component but for LLMs
  const [availableProviders, setAvailableProviders] = useState<string[]>([])
  useEffect(() => {
    EmbeddingModelsService.getAvailableProviders()
      .then((response) => {
        if (response && Array.isArray(response)) {
          setAvailableProviders(response)
          // If current provider is not in available list, set to first available
          if (modelProvider && !response.includes(modelProvider)) {
            setModelProvider(response[0] || "openai")
          }
        }
      })
      .catch((error) => {
        console.error("Failed to fetch available providers:", error)
        // Fallback to defaults
        setAvailableProviders(["huggingface", "openai", "ollama", "replicate", "aws"])
      })
  }, [])

  const [modelProvider, setModelProvider] = useState("openai")

  const { data: defaultModel } = useQuery({
    queryKey: ["defaultLlmModel"],
    queryFn: () => LlmModelsService.getDefaultLlmModel(),
  })

  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Query to fetch all LLMs
  const { data: modelsData, isLoading } = useQuery({
    queryKey: ["llmModels"],
    queryFn: () => LlmModelsService.getLlmModels(),
  })

  // Mutation to set a model as default
  const setDefaultMutation = useMutation({
    mutationFn: (modelId: string) => LlmModelsService.setDefaultLlmModel({ modelId }),
    onSuccess: () => {
      showSuccessToast("Default model updated successfully")
      queryClient.invalidateQueries({ queryKey: ["llmModels"] })
      queryClient.invalidateQueries({ queryKey: ["defaultLlmModel"] }) // <--- add this
    },
    onError: (error) => {
      showErrorToast(`Error updating default model: ${error.message}`)
    },
  })

  const handleSetDefault = (modelId: string) => {
    setDefaultMutation.mutate(modelId)
  }

  return (
    <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={6} bg="bg">
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>
            Large Language Models
          </Heading>
        </Box>

        <Show when={false}>
          <Button
            variant="solid"
            color="white"
            bg="rgba(0, 65, 72, 0.9)"
            _hover={{
              bg: "rgba(0, 65, 72, 0.85)",
            }}
            mb={6}
            onClick={() => {}}
          >
            <FiPlus />
            Add New LLM
          </Button>
        </Show>

        {isLoading ? (
          <Flex justify="center" align="center" h="200px">
            <Spinner size="lg" />
          </Flex>
        ) : !modelsData || modelsData.length === 0 ? (
          <EmptyState.Root>
            <EmptyState.Content>
              <EmptyState.Indicator>
                <FiSettings size={24} />
              </EmptyState.Indicator>
              <EmptyState.Title>No LLMs configured</EmptyState.Title>
              <EmptyState.Description>Add a new LLM to get started</EmptyState.Description>
            </EmptyState.Content>
          </EmptyState.Root>
        ) : (
          <Table.Root>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Name</Table.ColumnHeader>
                <Table.ColumnHeader>Provider</Table.ColumnHeader>
                <Table.ColumnHeader>Description</Table.ColumnHeader>
                <Table.ColumnHeader></Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {modelsData
                .filter(
                  (model): model is typeof model & { provider: string } =>
                    model.provider !== undefined &&
                    availableProviders.includes(model.provider.name),
                )
                .map((model) => (
                  <Table.Row key={model.id}>
                    <Table.Cell>{model.model_name}</Table.Cell>
                    <Table.Cell>
                      <Badge colorPalette={getProviderColor(model.provider)} size="sm">
                        {getProviderDisplayName(model.provider)}
                      </Badge>
                    </Table.Cell>
                    <Table.Cell>{model.description}</Table.Cell>
                    <Table.Cell textAlign="right">
                      {defaultModel?.id === model.id ? (
                        <Button
                          bg="rgba(0, 65, 72, 0.9)"
                          color="white"
                          size="xs"
                          width="full"
                          onClick={() => {}}
                        >
                          Default
                        </Button>
                      ) : (
                        <Button
                          size="xs"
                          bg="white"
                          color="rgba(0, 65, 72, 0.9)"
                          border="1px solid"
                          borderColor="rgba(0, 65, 72, 0.9)"
                          width="full"
                          _hover={{
                            bg: "rgba(0, 65, 72, 0.1)",
                          }}
                          onClick={() => model.id && handleSetDefault(model.id)}
                        >
                          Set as Default
                        </Button>
                      )}
                    </Table.Cell>
                  </Table.Row>
                ))}
            </Table.Body>
          </Table.Root>
        )}
      </VStack>
    </Box>
  )
}

function EmbeddingModels() {
  // Add state for available providers
  const [availableProviders, setAvailableProviders] = useState<string[]>([])

  // Fetch available providers when component mounts
  useEffect(() => {
    EmbeddingModelsService.getAvailableProviders()
      .then((response) => {
        if (response && Array.isArray(response)) {
          setAvailableProviders(response)
        }
      })
      .catch((error) => {
        console.error("Failed to fetch available providers:", error)
      })
  }, [])

  // Query to fetch all embedding models
  const { data: modelsData, isLoading } = useQuery({
    queryKey: ["embeddingModels"],
    queryFn: () => EmbeddingModelsService.getEmbeddingModelsRegistry(),
  })

  return (
    <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={6} bg="bg">
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>
            Embedding Models
          </Heading>
        </Box>

        <Show when={false}>
          <Button
            variant="solid"
            color="white"
            bg="rgba(0, 65, 72, 0.9)"
            _hover={{
              bg: "rgba(0, 65, 72, 0.85)",
            }}
            mb={6}
            onClick={() => {}}
          >
            <FiPlus />
            Add Embedding Model
          </Button>
        </Show>

        {isLoading ? (
          <Flex justify="center" align="center" h="200px">
            <Spinner size="lg" />
          </Flex>
        ) : !modelsData || modelsData.length === 0 ? (
          <EmptyState.Root>
            <EmptyState.Content>
              <EmptyState.Indicator>
                <FiSettings size={24} />
              </EmptyState.Indicator>
              <EmptyState.Title>No embedding models configured</EmptyState.Title>
              <EmptyState.Description>
                Add a new embedding model to get started
              </EmptyState.Description>
            </EmptyState.Content>
          </EmptyState.Root>
        ) : (
          <Table.Root>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Name</Table.ColumnHeader>
                <Table.ColumnHeader>Provider</Table.ColumnHeader>
                <Table.ColumnHeader>Description</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {modelsData
                .filter(
                  (model): model is typeof model & { provider: string } =>
                    model.provider !== undefined && availableProviders.includes(model.provider),
                )
                .map((model) => (
                  <Table.Row key={model.id}>
                    <Table.Cell>{model.model_name}</Table.Cell>
                    <Table.Cell>
                      <Badge colorPalette={getProviderColor(model.provider)} size="sm">
                        {getProviderDisplayName(model.provider)}
                      </Badge>
                    </Table.Cell>
                    <Table.Cell>{model.description}</Table.Cell>
                  </Table.Row>
                ))}
            </Table.Body>
          </Table.Root>
        )}
      </VStack>
    </Box>
  )
}
