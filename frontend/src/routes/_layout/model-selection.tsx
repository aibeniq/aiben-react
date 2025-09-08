import type { CancelablePromise } from "@/client/core/CancelablePromise"
import useCustomToast from "@/hooks/useCustomToast"
import {
  Badge,
  Box,
  Button,
  Container,
  Dialog,
  EmptyState,
  Flex,
  HStack,
  Heading,
  Input,
  Separator,
  Spinner,
  Table,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { FiCheckCircle, FiPlus, FiSettings, FiXCircle } from "react-icons/fi"
import { Field } from "../../components/ui/field"

// This will need to be added to your SDK client
import { EmbeddingModelsService, LlmModelsService } from "@/client"
import type { ModelProvider } from "@/client/types.gen"

export const Route = createFileRoute("/_layout/model-selection")({
  component: ModelSelection,
})

const getProviderDisplayName = (provider: string) => {
  switch (provider) {
    case "huggingface":
      return "HuggingFace"
    case "openai":
      return "OpenAI"
    case "ollama":
      return "Ollama"
    case "replicate":
      return "Replicate"
    case "aws":
      return "AWS Bedrock"
    default:
      return provider
  }
}

const getProviderColor = (provider: string) => {
  switch (provider) {
    case "huggingface":
      return "teal"
    case "openai":
      return "purple"
    case "ollama":
      return "orange"
    case "replicate":
      return "red"
    case "aws":
      return "blue"
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
        if (response.llm_providers && Array.isArray(response.llm_providers)) {
          setAvailableProviders(response.llm_providers)
          // If current provider is not in available list, set to first available
          if (
            modelProvider &&
            !response.llm_providers.includes(modelProvider)
          ) {
            setModelProvider(response.llm_providers[0] || "openai")
          }
        }
      })
      .catch((error) => {
        console.error("Failed to fetch available providers:", error)
        // Fallback to defaults
        setAvailableProviders([
          "huggingface",
          "openai",
          "ollama",
          "replicate",
          "aws",
        ])
      })
  }, [])

  const [isOpen, setIsOpen] = useState(false)
  const [modelName, setModelName] = useState("")
  const [modelId, setModelId] = useState("")
  const [modelDescription, setModelDescription] = useState("")
  const [modelProvider, setModelProvider] = useState("openai")

  const [isValidating, setIsValidating] = useState(false)
  const [isModelValid, setIsModelValid] = useState<boolean | null>(null)
  const [validationMessage, setValidationMessage] = useState("")

  const [isApiKeyConfigured, setIsApiKeyConfigured] = useState(true)

  const { data: defaultModel } = useQuery({
    queryKey: ["defaultLlmModel"],
    queryFn: () => LlmModelsService.getDefaultLlmModel(),
  })

  // Add this effect to check API key when provider changes
  useEffect(() => {
    if (modelProvider === "openai") {
      console.log("Checking OpenAI API key configuration...")
      EmbeddingModelsService.checkApiKeyConfigured({ provider: "openai" })
        .then((response) => {
          console.log("API key check succeeded:", response)
          setIsApiKeyConfigured(true)
        })
        .catch((error) => {
          console.error("API key check failed:", error)
          setIsApiKeyConfigured(false)
        })
    } else if (modelProvider === "aws") {
      console.log("Checking AWS credentials configuration...")
      EmbeddingModelsService.checkApiKeyConfigured({ provider: "aws" })
        .then((response) => {
          console.log("AWS credentials check succeeded:", response)
          setIsApiKeyConfigured(true)
        })
        .catch((error) => {
          console.error("AWS credentials check failed:", error)
          showErrorToast(
            "AWS credentials are not configured in the backend. Please add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to your environment.",
          )
          setIsApiKeyConfigured(false)
        })
    } else if (modelProvider === "ollama") {
      console.log("Checking Ollama server configuration...")
      EmbeddingModelsService.checkApiKeyConfigured({ provider: "ollama" })
        .then((response) => {
          console.log("Ollama server check succeeded:", response)
          setIsApiKeyConfigured(true)
        })
        .catch((error) => {
          console.error("Ollama server check failed:", error)
          showErrorToast(
            "Ollama server is not available. Please ensure Ollama is running.",
          )
          setIsApiKeyConfigured(false)
        })
    } else {
      setIsApiKeyConfigured(true)
    }
  }, [modelProvider])

  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Query to fetch all LLMs
  const { data: modelsData, isLoading } = useQuery({
    queryKey: ["llmModels"],
    queryFn: () => LlmModelsService.getLlmModels(),
  })

  // Add mutations for adding, updating, deleting models
  const addModelMutation = useMutation({
    mutationFn: (data: {
      name: string
      model_id: string
      provider: string
      description: string
    }) =>
      LlmModelsService.createLlmModel({
        requestBody: { ...data, provider: data.provider as any },
      }),
    onSuccess: () => {
      showSuccessToast("LLM added successfully")
      resetForm()
      setIsOpen(false)
      queryClient.invalidateQueries({ queryKey: ["llmModels"] })
      queryClient.invalidateQueries({ queryKey: ["defaultLlmModel"] })
    },
    onError: (error) => {
      showErrorToast(`Error adding LLM: ${error.message}`)
    },
  })

  // Mutation to set a model as default
  const setDefaultMutation = useMutation({
    mutationFn: (modelId: string) =>
      LlmModelsService.setDefaultLlmModel({ modelId }),
    onSuccess: () => {
      showSuccessToast("Default model updated successfully")
      queryClient.invalidateQueries({ queryKey: ["llmModels"] })
      queryClient.invalidateQueries({ queryKey: ["defaultLlmModel"] }) // <--- add this
    },
    onError: (error) => {
      showErrorToast(`Error updating default model: ${error.message}`)
    },
  })

  // Mutation to delete a model
  const deleteModelMutation = useMutation({
    mutationFn: (modelId: string) =>
      LlmModelsService.deleteLlmModel({ modelId }),
    onSuccess: () => {
      showSuccessToast("LLM deleted successfully")
      queryClient.invalidateQueries({ queryKey: ["llmModels"] })
    },
    onError: (error) => {
      showErrorToast(`Error deleting LLM: ${error.message}`)
    },
  })

  const handleValidateModel = async () => {
    if (!modelId.trim()) {
      setIsModelValid(false)
      setValidationMessage("Please enter a model ID")
      return
    }

    if (modelProvider === "openai" && !isApiKeyConfigured) {
      showErrorToast(
        "API key is required for OpenAI models and is not configured in the backend",
      )
      return
    }

    // Cancel any existing validation
    if (currentValidationRef.current) {
      currentValidationRef.current.cancel()
    }

    setIsValidating(true)

    const promise = LlmModelsService.validateLlmModel({
      requestBody: {
        model_id: modelId,
        provider: modelProvider as any,
      },
    })

    currentValidationRef.current = promise

    try {
      await promise
      setIsModelValid(true)
      setValidationMessage("Model is valid and can be loaded.")
    } catch (error: any) {
      // Only show error if it's not a cancellation
      if (error.name !== "CancelError") {
        setIsModelValid(false)
        setValidationMessage(`Invalid model: ${error.message}`)
      }
    } finally {
      // Only reset if this is still the current validation
      if (currentValidationRef.current === promise) {
        setIsValidating(false)
        currentValidationRef.current = null
      }
    }
  }

  const resetForm = () => {
    setModelName("")
    setModelId("")
    setModelDescription("")
    setModelProvider("openai")
  }

  const handleAddModel = () => {
    if (!modelName.trim() || !modelId.trim()) {
      showErrorToast("Please fill in all required fields")
      return
    }

    // Only check for API key if it's not configured in the backend
    if (modelProvider === "openai" && !isApiKeyConfigured) {
      showErrorToast(
        "API key is required for OpenAI models and is not configured in the backend",
      )
      return
    }

    addModelMutation.mutate({
      name: modelName,
      model_id: modelId,
      provider: modelProvider,
      description: modelDescription,
    })
  }

  const handleSetDefault = (modelId: string) => {
    setDefaultMutation.mutate(modelId)
  }

  const handleDeleteModel = (modelId: string) => {
    if (confirm("Are you sure you want to delete this LLM?")) {
      deleteModelMutation.mutate(modelId)
    }
  }

  // Add a reference to store current validation promise
  const currentValidationRef = useRef<CancelablePromise<any> | null>(null)

  // Clean up any pending validations when component unmounts
  useEffect(() => {
    return () => {
      if (currentValidationRef.current) {
        currentValidationRef.current.cancel()
        currentValidationRef.current = null
      }
    }
  }, [])

  // Modify the Dialog to handle validation cancellation
  const handleModalClose = () => {
    // Cancel any pending validation
    if (currentValidationRef.current) {
      currentValidationRef.current.cancel()
      currentValidationRef.current = null
    }

    // Reset form state
    resetForm()
    setIsValidating(false)
    setIsModelValid(null)

    // Close the modal
    setIsOpen(false)
  }

  return (
    <Box
      border="1px solid"
      borderColor="gray.200"
      borderRadius="md"
      p={6}
      bg="bg"
    >
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>
            LLM Management
          </Heading>
          <Text mb={4}>
            Configure and manage the LLMs used for generating text responses.
            The default model will be used for all operations.
          </Text>
        </Box>

        <Button
          variant="solid"
          color="white"
          bg="rgba(0, 65, 72, 0.9)"
          _hover={{
            bg: "rgba(0, 65, 72, 0.85)",
          }}
          mb={6}
          onClick={() => {
            resetForm()
            setIsOpen(true)
          }}
        >
          <FiPlus />
          Add New LLM
        </Button>

        {isLoading ? (
          <Flex justify="center" align="center" h="200px">
            <Spinner size="lg" />
          </Flex>
        ) : !modelsData || modelsData.data.length === 0 ? (
          <EmptyState.Root>
            <EmptyState.Content>
              <EmptyState.Indicator>
                <FiSettings size={24} />
              </EmptyState.Indicator>
              <EmptyState.Title>No LLMs configured</EmptyState.Title>
              <EmptyState.Description>
                Add a new LLM to get started
              </EmptyState.Description>
            </EmptyState.Content>
          </EmptyState.Root>
        ) : (
          <Table.Root>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Name</Table.ColumnHeader>
                <Table.ColumnHeader>Model ID</Table.ColumnHeader>
                <Table.ColumnHeader>Provider</Table.ColumnHeader>
                <Table.ColumnHeader>Description</Table.ColumnHeader>
                <Table.ColumnHeader>Status</Table.ColumnHeader>
                <Table.ColumnHeader>Actions</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {modelsData.data
                .filter(
                  (model): model is typeof model & { provider: string } =>
                    model.provider !== undefined &&
                    availableProviders.includes(model.provider),
                )
                .map((model) => (
                  <Table.Row key={model.id}>
                    <Table.Cell>{model.name}</Table.Cell>
                    <Table.Cell>
                      <code>{model.model_id}</code>
                    </Table.Cell>
                    <Table.Cell>
                      <Badge
                        colorPalette={getProviderColor(model.provider)}
                        size="sm"
                      >
                        {getProviderDisplayName(model.provider)}
                      </Badge>
                    </Table.Cell>
                    <Table.Cell>{model.description}</Table.Cell>
                    <Table.Cell>
                      {defaultModel?.id === model.id ? (
                        <Badge colorPalette="green" size="sm">
                          Default
                        </Badge>
                      ) : (
                        <Badge colorPalette="gray" size="sm">
                          Available
                        </Badge>
                      )}
                    </Table.Cell>
                    <Table.Cell>
                      <HStack gap={2}>
                        {defaultModel?.id !== model.id && (
                          <Button
                            size="xs"
                            colorPalette="blue"
                            onClick={() =>
                              model.id && handleSetDefault(model.id)
                            }
                          >
                            Set as Default
                          </Button>
                        )}
                        {model.owner_id && (
                          <Button
                            size="xs"
                            colorPalette="red"
                            onClick={() =>
                              model.id && handleDeleteModel(model.id)
                            }
                          >
                            Delete
                          </Button>
                        )}
                      </HStack>
                    </Table.Cell>
                  </Table.Row>
                ))}
            </Table.Body>
          </Table.Root>
        )}

        <Dialog.Root
          open={isOpen}
          onOpenChange={(details) => {
            if (!details.open) {
              handleModalClose()
            } else {
              setIsOpen(true)
            }
          }}
        >
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Box position="relative">
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    handleAddModel()
                  }}
                >
                  <Dialog.Header>
                    <Dialog.Title>Add New LLM</Dialog.Title>
                  </Dialog.Header>
                  <Dialog.Body>
                    <VStack gap={4}>
                      <Field label="Display Name" required>
                        <Input
                          value={modelName}
                          onChange={(e) => setModelName(e.target.value)}
                          placeholder="e.g., My Custom Model"
                        />
                      </Field>

                      <Field label="Provider" required>
                        <select
                          value={modelProvider}
                          onChange={(e) => setModelProvider(e.target.value)}
                          style={{
                            width: "100%",
                            padding: "0.5rem",
                            borderRadius: "0.375rem",
                            borderColor: "#E2E8F0",
                            fontSize: "1rem",
                            height: "2.5rem",
                          }}
                        >
                          {availableProviders.map((provider) => (
                            <option key={provider} value={provider}>
                              {provider === "huggingface"
                                ? "HuggingFace"
                                : provider === "openai"
                                  ? "OpenAI"
                                  : provider === "ollama"
                                    ? "Ollama"
                                    : provider === "replicate"
                                      ? "Replicate"
                                      : provider === "aws"
                                        ? "AWS Bedrock"
                                        : provider}
                            </option>
                          ))}
                        </select>
                      </Field>

                      <Field label="Model ID" required>
                        <HStack>
                          <Input
                            value={modelId}
                            onChange={(e) => {
                              setModelId(e.target.value)
                              setIsModelValid(null)
                            }}
                            placeholder="e.g., sentence-transformers/all-MiniLM-L6-v2"
                          />
                          <Button
                            onClick={handleValidateModel}
                            loading={isValidating}
                            loadingText="Validating"
                            disabled={!modelId.trim()}
                            variant="outline"
                            color="rgba(0, 65, 72, 0.9)"
                            borderColor="rgba(0, 65, 72, 0.9)"
                            _hover={{
                              bg: "gray.100",
                            }}
                          >
                            {isValidating ? <Spinner size="sm" /> : "Validate"}
                          </Button>
                        </HStack>
                        {isModelValid !== null && (
                          <Box
                            mt={2}
                            p={2}
                            borderRadius="md"
                            bg={isModelValid ? "green.50" : "red.50"}
                            color={isModelValid ? "green.700" : "red.700"}
                          >
                            <HStack>
                              <Box>
                                {isModelValid ? (
                                  <FiCheckCircle />
                                ) : (
                                  <FiXCircle />
                                )}
                              </Box>
                              <Text fontSize="sm">{validationMessage}</Text>
                            </HStack>
                          </Box>
                        )}
                      </Field>

                      <Field label="Description">
                        <Textarea
                          value={modelDescription}
                          onChange={(e) => setModelDescription(e.target.value)}
                          placeholder="Describe the model, its characteristics, and when to use it"
                          rows={3}
                        />
                      </Field>
                    </VStack>
                  </Dialog.Body>
                  <Dialog.Footer gap={2}>
                    <Dialog.ActionTrigger asChild>
                      <Button variant="subtle" colorPalette="gray">
                        Cancel
                      </Button>
                    </Dialog.ActionTrigger>
                    <Button
                      variant="solid"
                      color="white"
                      bg="rgba(0, 65, 72, 0.9)"
                      _hover={{
                        bg: "rgba(0, 65, 72, 0.85)",
                      }}
                      type="submit"
                      disabled={!isModelValid}
                    >
                      Add Model
                    </Button>
                  </Dialog.Footer>
                </form>
              </Box>
              <Dialog.CloseTrigger />
            </Dialog.Content>
          </Dialog.Positioner>
        </Dialog.Root>
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
        if (
          response.embedding_providers &&
          Array.isArray(response.embedding_providers)
        ) {
          setAvailableProviders(response.embedding_providers)
          // If current provider is not in available list, set to first available
          if (
            modelProvider &&
            !response.embedding_providers.includes(modelProvider)
          ) {
            setModelProvider(response.embedding_providers[0] || "openai")
          }
        }
      })
      .catch((error) => {
        console.error("Failed to fetch available providers:", error)
        // Fallback to defaults
        setAvailableProviders([
          "huggingface",
          "openai",
          "ollama",
          "replicate",
          "aws",
        ])
      })
  }, [])

  // Update state management
  const [isOpen, setIsOpen] = useState(false)

  // Update onOpen and onClose functions
  const onOpen = () => setIsOpen(true)
  const onClose = () => setIsOpen(false)
  const [modelName, setModelName] = useState("")
  const [modelId, setModelId] = useState("")
  const [modelDescription, setModelDescription] = useState("")
  const [isValidating, setIsValidating] = useState(false)
  const [isModelValid, setIsModelValid] = useState<boolean | null>(null)
  const [validationMessage, setValidationMessage] = useState("")

  const [modelProvider, setModelProvider] = useState("openai")

  const [isApiKeyConfigured, setIsApiKeyConfigured] = useState(true)

  const { data: defaultModel } = useQuery({
    queryKey: ["defaultEmbeddingModel"],
    queryFn: () => EmbeddingModelsService.getDefaultEmbeddingModel(),
  })

  // Add this effect to check API key when provider changes
  useEffect(() => {
    if (modelProvider === "openai") {
      console.log("Checking API key configuration for OpenAI...")
      // Check if API key is configured in backend
      EmbeddingModelsService.checkApiKeyConfigured({ provider: "openai" })
        .then((response) => {
          console.log("API key check succeeded:", response)
          setIsApiKeyConfigured(true)
        })
        .catch((error) => {
          console.error("API key check failed:", error) // Log the detailed error
          console.log("Error response:", error.response) // Detailed error response if available
          console.log("Error message:", error.message)
          console.log("Error status:", error.status)
          setIsApiKeyConfigured(false)
        })
    } else {
      setIsApiKeyConfigured(true)
    }
  }, [modelProvider])

  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const resetForm = () => {
    setModelName("")
    setModelId("")
    setModelDescription("")
    setIsModelValid(null)
    setValidationMessage("")
  }

  // Query to fetch all embedding models
  const { data: modelsData, isLoading } = useQuery({
    queryKey: ["embeddingModels"],
    queryFn: () => EmbeddingModelsService.getEmbeddingModels(),
  })

  // Mutation to add a new model
  const addModelMutation = useMutation({
    mutationFn: (data: {
      name: string
      model_id: string
      provider: string
      description: string
    }) => {
      console.log("Sending data to createEmbeddingModel:", data)
      return EmbeddingModelsService.createEmbeddingModel({
        requestBody: { ...data, provider: data.provider as ModelProvider },
      })
        .then((response) => {
          console.log("Received successful response:", response)
          return response
        })
        .catch((error) => {
          console.error("Received error response:", error)
          throw error
        })
    },
    onSuccess: (data) => {
      console.log("Mutation completed successfully with data:", data)
      showSuccessToast("Model added successfully")
      resetForm()
      onClose()
      queryClient.invalidateQueries({ queryKey: ["embeddingModels"] })
    },
    onError: (error) => {
      console.error("Mutation failed with error:", error)
      showErrorToast(`Error adding model: ${error.message}`)
    },
  })

  // Mutation to validate a model
  const validateModelMutation = useMutation({
    mutationFn: (data: {
      requestBody: { model_id: string; provider: string }
    }) => {
      console.log(
        "The following data will be sent to the server for model validation:",
        data,
      )
      return EmbeddingModelsService.validateEmbeddingModel({
        requestBody: {
          ...data.requestBody,
          provider: data.requestBody.provider as ModelProvider,
        },
      })
    },
    onSuccess: () => {
      setIsModelValid(true)
      setValidationMessage("Model is valid and can be loaded.")
    },
    onError: (error) => {
      setIsModelValid(false)
      setValidationMessage(`Invalid model: ${error.message}`)
    },
    onSettled: () => {
      setIsValidating(false)
    },
  })

  // Mutation to set a model as default
  const setDefaultMutation = useMutation({
    mutationFn: (modelId: string) =>
      EmbeddingModelsService.setDefaultEmbeddingModel({ modelId }),
    onSuccess: () => {
      showSuccessToast("Default model updated successfully")
      queryClient.invalidateQueries({ queryKey: ["embeddingModels"] })
      queryClient.invalidateQueries({ queryKey: ["defaultEmbeddingModel"] })
    },
    onError: (error) => {
      showErrorToast(`Error updating default model: ${error.message}`)
    },
  })

  // Mutation to delete a model
  const deleteModelMutation = useMutation({
    mutationFn: (modelId: string) =>
      EmbeddingModelsService.deleteEmbeddingModel({ modelId }),
    onSuccess: () => {
      showSuccessToast("Model deleted successfully")
      queryClient.invalidateQueries({ queryKey: ["embeddingModels"] })
    },
    onError: (error) => {
      showErrorToast(`Error deleting model: ${error.message}`)
    },
  })

  // Handler for model validation
  const handleValidateModel = async () => {
    if (!modelId.trim()) {
      setIsModelValid(false)
      setValidationMessage("Please enter a model ID")
      return
    }

    if (modelProvider === "openai" && !isApiKeyConfigured) {
      showErrorToast(
        "API key is required for OpenAI models and is not configured in the backend",
      )
      return
    }

    setIsValidating(true)
    console.log(
      "Validating model with ID:",
      modelId,
      "and provider:",
      modelProvider,
    )
    validateModelMutation.mutate({
      requestBody: {
        model_id: modelId,
        provider: modelProvider,
      },
    })
  }

  // Handler for model submission
  const handleAddModel = () => {
    if (!modelName.trim() || !modelId.trim()) {
      showErrorToast("Please fill in all required fields")
      return
    }

    if (modelProvider === "openai" && !isApiKeyConfigured) {
      showErrorToast(
        "API key is required for OpenAI models and is not configured in the backend",
      )
      return
    }

    addModelMutation.mutate({
      name: modelName,
      model_id: modelId,
      provider: modelProvider,
      description: modelDescription,
    })
  }

  // Handler for setting a model as default
  const handleSetDefault = (modelId: string) => {
    setDefaultMutation.mutate(modelId)
  }

  // Handler for deleting a model
  const handleDeleteModel = (modelId: string) => {
    if (confirm("Are you sure you want to delete this model?")) {
      deleteModelMutation.mutate(modelId)
    }
  }

  return (
    <Box
      border="1px solid"
      borderColor="gray.200"
      borderRadius="md"
      p={6}
      bg="bg"
    >
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>
            Embedding Model Management
          </Heading>
          <Text mb={4}>
            Configure and manage the embedding models used for knowledge base
            indexing and retrieval. The default model will be used when creating
            new knowledge bases, but each knowledge base will continue using its
            original embedding model even if the default changes later.
          </Text>
        </Box>

        <Button
          variant="solid"
          color="white"
          bg="rgba(0, 65, 72, 0.9)"
          _hover={{
            bg: "rgba(0, 65, 72, 0.85)",
          }}
          mb={6}
          onClick={() => {
            resetForm()
            onOpen()
          }}
        >
          <FiPlus />
          Add Embedding Model
        </Button>

        {isLoading ? (
          <Flex justify="center" align="center" h="200px">
            <Spinner size="lg" />
          </Flex>
        ) : !modelsData || modelsData.data.length === 0 ? (
          <EmptyState.Root>
            <EmptyState.Content>
              <EmptyState.Indicator>
                <FiSettings size={24} />
              </EmptyState.Indicator>
              <EmptyState.Title>
                No embedding models configured
              </EmptyState.Title>
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
                <Table.ColumnHeader>Model ID</Table.ColumnHeader>
                <Table.ColumnHeader>Provider</Table.ColumnHeader>
                <Table.ColumnHeader>Description</Table.ColumnHeader>
                <Table.ColumnHeader>Status</Table.ColumnHeader>
                <Table.ColumnHeader>Actions</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {modelsData.data
                .filter(
                  (model): model is typeof model & { provider: string } =>
                    model.provider !== undefined &&
                    availableProviders.includes(model.provider),
                )
                .map((model) => (
                  <Table.Row key={model.id}>
                    <Table.Cell>{model.name}</Table.Cell>
                    <Table.Cell>
                      <code>{model.model_id}</code>
                    </Table.Cell>
                    <Table.Cell>
                      <Badge
                        colorPalette={getProviderColor(model.provider)}
                        size="sm"
                      >
                        {getProviderDisplayName(model.provider)}
                      </Badge>
                    </Table.Cell>
                    <Table.Cell>{model.description}</Table.Cell>
                    <Table.Cell>
                      {defaultModel?.id === model.id ? (
                        <Badge colorPalette="green" size="sm">
                          Default
                        </Badge>
                      ) : (
                        <Badge colorPalette="gray" size="sm">
                          Available
                        </Badge>
                      )}
                    </Table.Cell>
                    <Table.Cell>
                      <HStack gap={2}>
                        {defaultModel?.id !== model.id && (
                          <Button
                            size="xs"
                            colorPalette="blue"
                            onClick={() =>
                              model.id && handleSetDefault(model.id)
                            }
                          >
                            Set as Default
                          </Button>
                        )}
                        {model.owner_id && (
                          <Button
                            size="xs"
                            colorPalette="red"
                            onClick={() =>
                              model.id && handleDeleteModel(model.id)
                            }
                          >
                            Delete
                          </Button>
                        )}
                      </HStack>
                    </Table.Cell>
                  </Table.Row>
                ))}
            </Table.Body>
          </Table.Root>
        )}
        {/* Dialog for adding a new embedding model */}
        <Dialog.Root
          open={isOpen}
          onOpenChange={(details) => setIsOpen(details.open)}
        >
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Box position="relative">
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    handleAddModel()
                  }}
                >
                  <Dialog.Header>
                    <Dialog.Title>Add Embedding Model</Dialog.Title>
                  </Dialog.Header>
                  <Dialog.Body>
                    <VStack gap={4}>
                      <Field label="Display Name" required>
                        <Input
                          value={modelName}
                          onChange={(e) => setModelName(e.target.value)}
                          placeholder="e.g., My Custom Model"
                        />
                      </Field>

                      <Field label="Provider" required>
                        <select
                          value={modelProvider}
                          onChange={(e) => setModelProvider(e.target.value)}
                          style={{
                            width: "100%",
                            padding: "0.5rem",
                            borderRadius: "0.375rem",
                            borderColor: "#E2E8F0",
                            fontSize: "1rem",
                            height: "2.5rem",
                          }}
                        >
                          {availableProviders.map((provider) => (
                            <option key={provider} value={provider}>
                              {provider === "huggingface"
                                ? "HuggingFace"
                                : provider === "openai"
                                  ? "OpenAI"
                                  : provider === "ollama"
                                    ? "Ollama"
                                    : provider === "replicate"
                                      ? "Replicate"
                                      : provider === "aws"
                                        ? "AWS Bedrock"
                                        : provider}
                            </option>
                          ))}
                        </select>
                      </Field>

                      <Field label="Model ID" required>
                        <HStack>
                          <Input
                            value={modelId}
                            onChange={(e) => {
                              setModelId(e.target.value)
                              setIsModelValid(null)
                            }}
                            placeholder="e.g., sentence-transformers/all-MiniLM-L6-v2"
                          />
                          <Button
                            onClick={handleValidateModel}
                            loading={isValidating}
                            loadingText="Validating"
                            disabled={!modelId.trim()}
                            variant="outline"
                            color="rgba(0, 65, 72, 0.9)"
                            borderColor="rgba(0, 65, 72, 0.9)"
                            _hover={{
                              bg: "gray.100",
                            }}
                          >
                            {isValidating ? <Spinner size="sm" /> : "Validate"}
                          </Button>
                        </HStack>
                        {isModelValid !== null && (
                          <Box
                            mt={2}
                            p={2}
                            borderRadius="md"
                            bg={isModelValid ? "green.50" : "red.50"}
                            color={isModelValid ? "green.700" : "red.700"}
                          >
                            <HStack>
                              <Box>
                                {isModelValid ? (
                                  <FiCheckCircle />
                                ) : (
                                  <FiXCircle />
                                )}
                              </Box>
                              <Text fontSize="sm">{validationMessage}</Text>
                            </HStack>
                          </Box>
                        )}
                      </Field>

                      <Field label="Description">
                        <Textarea
                          value={modelDescription}
                          onChange={(e) => setModelDescription(e.target.value)}
                          placeholder="Describe the model, its characteristics, and when to use it"
                          rows={3}
                        />
                      </Field>
                    </VStack>
                  </Dialog.Body>
                  <Dialog.Footer gap={2}>
                    <Dialog.ActionTrigger asChild>
                      <Button variant="subtle" colorPalette="gray">
                        Cancel
                      </Button>
                    </Dialog.ActionTrigger>
                    <Button
                      variant="solid"
                      color="white"
                      bg="rgba(0, 65, 72, 0.9)"
                      _hover={{
                        bg: "rgba(0, 65, 72, 0.85)",
                      }}
                      type="submit"
                      disabled={!isModelValid}
                    >
                      Add Model
                    </Button>
                  </Dialog.Footer>
                </form>
              </Box>
              <Dialog.CloseTrigger />
            </Dialog.Content>
          </Dialog.Positioner>
        </Dialog.Root>
      </VStack>
    </Box>
  )
}
