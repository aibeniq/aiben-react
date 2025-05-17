import {
  Box,
  Button,
  Container,
  EmptyState,
  Flex,
  Heading,
  HStack,
  Input,
  Dialog,
  SimpleGrid,
  Spinner,
  Table,
  Badge,
  Text,
  Textarea,
  useDisclosure,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { FiPlus, FiSettings, FiCheckCircle, FiXCircle } from "react-icons/fi"
import { Field } from "../../components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"

// This will need to be added to your SDK client
import { EmbeddingModelsService } from "@/client"

export const Route = createFileRoute("/_layout/model-selection")({
  component: EmbeddingModels,
})

function EmbeddingModels() {
  // Update your state management
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

  const [modelProvider, setModelProvider] = useState("huggingface")
  const [apiKey, setApiKey] = useState("")
  
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
    mutationFn: (data: { name: string; model_id: string; description: string }) =>
      EmbeddingModelsService.createEmbeddingModel({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Model added successfully")
      resetForm()
      onClose()
      queryClient.invalidateQueries({ queryKey: ["embeddingModels"] })
    },
    onError: (error) => {
      showErrorToast(`Error adding model: ${error.message}`)
    },
  })
  
  // Mutation to validate a model
  const validateModelMutation = useMutation({
    mutationFn: (modelId: string) =>
      EmbeddingModelsService.validateEmbeddingModel({ requestBody: {
        model_id: modelId
      } }),
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
    
    setIsValidating(true)
    validateModelMutation.mutate({
        model_id: modelId,
        provider: modelProvider,
        api_key: modelProvider === "openai" ? apiKey : undefined
    })
  }
  
  // Handler for model submission
    const handleAddModel = () => {
    if (!modelName.trim() || !modelId.trim()) {
        showErrorToast("Please fill in all required fields")
        return
    }
    
    if (modelProvider === "openai" && !apiKey.trim()) {
        showErrorToast("API key is required for OpenAI models")
        return
    }
    
    addModelMutation.mutate({
        name: modelName,
        model_id: modelId,
        provider: modelProvider,
        description: modelDescription,
        api_key: modelProvider === "openai" ? apiKey : undefined
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
    <Container maxW="full">
      <Heading size="lg" pt={12} mb={6}>
        Embedding Model Management
      </Heading>
      
      <Text mb={4}>
        Configure and manage the embedding models used for knowledge base indexing and retrieval.
        The default model will be used for all new knowledge bases and RAG operations.
      </Text>
      
      <Button
        leftIcon={<FiPlus />}
        colorPalette="blue"
        mb={6}
        onClick={() => {
          resetForm()
          onOpen()
        }}
      >
        Add New Embedding Model
      </Button>
      
      {isLoading ? (
        <Flex justify="center" align="center" h="200px">
          <Spinner size="lg" />
        </Flex>
      ) : !modelsData || modelsData.data.length === 0 ? (
        <EmptyState.Root>
          <EmptyState.Content>
            <EmptyState.Icon>
              <FiSettings size={24} />
            </EmptyState.Icon>
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
              <Table.ColumnHeader>Model ID</Table.ColumnHeader>
              <Table.ColumnHeader>Description</Table.ColumnHeader>
              <Table.ColumnHeader>Status</Table.ColumnHeader>
              <Table.ColumnHeader>Actions</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {modelsData.data.map((model) => (
              <Table.Row key={model.id}>
                <Table.Cell>{model.name}</Table.Cell>
                <Table.Cell>
                  <code>{model.model_id}</code>
                </Table.Cell>
                <Table.Cell>{model.description}</Table.Cell>
                <Table.Cell>
                  {model.is_default ? (
                        <Badge colorPalette="green" size="sm">Default</Badge>
                    ) : (
                        <Badge colorPalette="gray" size="sm">Available</Badge>
                    )}
                </Table.Cell>
                <Table.Cell>
                  <HStack spacing={2}>
                    {!model.is_default && (
                      <Button
                        size="xs"
                        colorPalette="blue"
                        onClick={() => handleSetDefault(model.id)}
                      >
                        Set as Default
                      </Button>
                    )}
                    {model.owner_id && (
                      <Button
                        size="xs"
                        colorPalette="red"
                        onClick={() => handleDeleteModel(model.id)}
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
      
      {/* Dialog for adding a new model */}
        <Dialog.Root open={isOpen} onOpenChange={(details) => setIsOpen(details.open)}>
        <Dialog.Backdrop />
        <Dialog.Positioner>
            <Dialog.Content size="lg">
            <Dialog.Header>Add New Embedding Model</Dialog.Header>
            <Dialog.CloseTrigger />
            <Dialog.Body>
                <VStack spacing={4} align="stretch">
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
                >
                    <option value="huggingface">HuggingFace</option>
                    <option value="openai">OpenAI</option>
                </select>
                </Field>
                
                <Field label="Model ID" required>
                    <HStack>
                    <Input
                        value={modelId}
                        onChange={(e) => {
                        setModelId(e.target.value);
                        setIsModelValid(null);
                        }}
                        placeholder="e.g., sentence-transformers/all-MiniLM-L6-v2"
                    />
                    <Button
                        onClick={handleValidateModel}
                        isLoading={isValidating}
                        loadingText="Validating"
                    >
                        Validate
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
                            {isModelValid ? <FiCheckCircle /> : <FiXCircle />}
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
            
            <Dialog.Footer>
                <Button variant="outline" mr={3} onClick={() => setIsOpen(false)}>
                Cancel
                </Button>
                <Button
                colorPalette="blue"
                onClick={handleAddModel}
                isDisabled={!isModelValid}
                >
                Add Model
                </Button>
            </Dialog.Footer>
            </Dialog.Content>
        </Dialog.Positioner>
        </Dialog.Root>
    </Container>
  )
}