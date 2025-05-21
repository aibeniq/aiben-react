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
  Separator,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState, useEffect } from "react"
import { FiPlus, FiSettings, FiCheckCircle, FiXCircle } from "react-icons/fi"
import { Field } from "../../components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"

// This will need to be added to your SDK client
import { LlmModelsService, EmbeddingModelsService } from "@/client"

export const Route = createFileRoute("/_layout/model-selection")({
  component: ModelSelection,
})

function ModelSelection() {
  return (
    <Container maxW="full">
      {/* First section: Embedding Models */}
      <EmbeddingModels />
      
      {/* Divider between sections */}
      <Separator my={10} />
      
      {/* Second section: LLMs */}
      <LlmModels />
    </Container>
  );
}

function LlmModels() {
  // Similar to your EmbeddingModels component but for LLMs
  const [isOpen, setIsOpen] = useState(false);
  const [modelName, setModelName] = useState("");
  const [modelId, setModelId] = useState("");
  const [modelDescription, setModelDescription] = useState("");
  const [modelProvider, setModelProvider] = useState("openai");

  const [isValidating, setIsValidating] = useState(false);
  const [isModelValid, setIsModelValid] = useState<boolean | null>(null);
  const [validationMessage, setValidationMessage] = useState("");

  const [isApiKeyConfigured, setIsApiKeyConfigured] = useState(true);

  // Add this effect to check API key when provider changes
  useEffect(() => {
    if (modelProvider === "openai") {
      // Check if API key is configured in backend
      EmbeddingModelsService.checkApiKeyConfigured({provider: "openai"})
        .then(() => {
          setIsApiKeyConfigured(true);
        })
        .catch(() => {
          setIsApiKeyConfigured(false);
        });
    } else {
      setIsApiKeyConfigured(true);
    }
  }, [modelProvider]);
  
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  
  // Query to fetch all LLMs
  const { data: modelsData, isLoading } = useQuery({
    queryKey: ["llmModels"],
    queryFn: () => LlmModelsService.getLlmModels(),
  });

  // Add mutations for adding, updating, deleting models
  const addModelMutation = useMutation({
    mutationFn: (data: { name: string; model_id: string; provider: string; description: string }) =>
      LlmModelsService.createLlmModel({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("LLM added successfully")
      resetForm()
      setIsOpen(false)
      queryClient.invalidateQueries({ queryKey: ["llmModels"] })
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
      showSuccessToast("Default LLM updated successfully")
      queryClient.invalidateQueries({ queryKey: ["llmModels"] })
    },
    onError: (error) => {
      showErrorToast(`Error updating default LLM: ${error.message}`)
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

  // Mutation to validate a model
  const validateModelMutation = useMutation({
    mutationFn: (data: { requestBody: { model_id: string; provider: string } }) => {
    console.log("The following data will be sent to the server for model validation:", data);
    return LlmModelsService.validateLlmModel(data);
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

  const handleValidateModel = () => {
    if (!modelId.trim()) {
      setIsModelValid(false);
      setValidationMessage("Please enter a model ID");
      return;
    }

    if (modelProvider === "openai" && !isApiKeyConfigured) {
          showErrorToast("API key is required for OpenAI models and is not configured in the backend");
          return;
        }

    setIsValidating(true);
    validateModelMutation.mutate({
      requestBody: {
      model_id: modelId,
      provider: modelProvider
    }
    });
  };

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
      showErrorToast("API key is required for OpenAI models and is not configured in the backend");
      return;
    }
    
    addModelMutation.mutate({
      name: modelName,
      model_id: modelId,
      provider: modelProvider,
      description: modelDescription
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
  
  return (
    <>
      <Heading size="lg" mb={6}>
        LLM Management
      </Heading>
      
      <Text mb={4}>
        Configure and manage the LLMs used for processing tasks.
        The default model will be used for all operations.
      </Text>
      
      <Button
        leftIcon={<FiPlus />}
        colorPalette="blue"
        mb={6}
        onClick={() => {
          resetForm()
          setIsOpen(true)
        }}
      >
        Add New LLM
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
            {modelsData.data.map((model) => (
              <Table.Row key={model.id}>
                <Table.Cell>{model.name}</Table.Cell>
                <Table.Cell>
                  <code>{model.model_id}</code>
                </Table.Cell>
                <Table.Cell>{model.provider}</Table.Cell>
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
      
      {/* Dialog for adding a new LLM */}
        <Dialog.Root open={isOpen} onOpenChange={(details) => setIsOpen(details.open)}>
          <Dialog.Backdrop />
          <Dialog.Positioner>
          <Dialog.Content size={{ base: "xs", md: "md" }} placement="center">
            <Box position="relative">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAddModel();
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
                          width: '100%',
                          padding: '0.5rem',
                          borderRadius: '0.375rem',
                          borderColor: '#E2E8F0',
                          fontSize: '1rem',
                          height: '2.5rem',                          
                        }}
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
                          disabled={!modelId.trim()}
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
                <Dialog.Footer gap={2}>
                  <Dialog.ActionTrigger asChild>
                    <Button variant="subtle" colorPalette="gray">
                      Cancel
                    </Button>
                  </Dialog.ActionTrigger>
                  <Button
                    colorPalette="blue"
                    type="submit"
                    isDisabled={!isModelValid}
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
    </>
  );
}


function EmbeddingModels() {
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

  const [modelProvider, setModelProvider] = useState("huggingface")

  const [isApiKeyConfigured, setIsApiKeyConfigured] = useState(true);

  // Add this effect to check API key when provider changes
  useEffect(() => {
    if (modelProvider === "openai") {
      console.log("Checking API key configuration for OpenAI...");
      // Check if API key is configured in backend
      EmbeddingModelsService.checkApiKeyConfigured({provider: "openai"})
        .then((response) => {
          console.log("API key check succeeded:", response);
          setIsApiKeyConfigured(true);
        })
        .catch((error) => {
          console.error("API key check failed:", error); // Log the detailed error
          console.log("Error response:", error.response); // Detailed error response if available
          console.log("Error message:", error.message);
          console.log("Error status:", error.status);
          setIsApiKeyConfigured(false);
        });
    } else {
      setIsApiKeyConfigured(true);
    }
  }, [modelProvider]);
  
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
    mutationFn: (data: { name: string; model_id: string; provider: string; description: string }) => {
      console.log("Sending data to createEmbeddingModel:", data);
      return EmbeddingModelsService.createEmbeddingModel({ requestBody: data })
        .then(response => {
          console.log("Received successful response:", response);
          return response;
        })
        .catch(error => {
          console.error("Received error response:", error);
          throw error;
        });
    },
    onSuccess: (data) => {
      console.log("Mutation completed successfully with data:", data);
      showSuccessToast("Model added successfully");
      resetForm();
      onClose();
      queryClient.invalidateQueries({ queryKey: ["embeddingModels"] });
    },
    onError: (error) => {
      console.error("Mutation failed with error:", error);
      showErrorToast(`Error adding model: ${error.message}`);
    },
  })
  
  // Mutation to validate a model
  const validateModelMutation = useMutation({
    mutationFn: (data: { requestBody: { model_id: string; provider: string } }) => {
    console.log("The following data will be sent to the server for model validation:", data);
    return EmbeddingModelsService.validateEmbeddingModel(data);
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
      showErrorToast("API key is required for OpenAI models and is not configured in the backend");
      return;
    }
    
    setIsValidating(true)
    validateModelMutation.mutate({
      requestBody: {  
        model_id: modelId,
        provider: modelProvider
      }
    })
  }
  
  // Handler for model submission
    const handleAddModel = () => {
    if (!modelName.trim() || !modelId.trim()) {
        showErrorToast("Please fill in all required fields")
        return
    }
    
    if (modelProvider === "openai" && !isApiKeyConfigured) {
      showErrorToast("API key is required for OpenAI models and is not configured in the backend");
      return;
    }
    
    addModelMutation.mutate({
        name: modelName,
        model_id: modelId,
        provider: modelProvider,
        description: modelDescription
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
    <>
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
              <Table.ColumnHeader>Provider</Table.ColumnHeader>
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
                <Table.Cell>
                  <Badge 
                    colorPalette={model.provider === "huggingface" ? "teal" : "purple"} 
                    size="sm"
                  >
                    {model.provider === "huggingface" ? "HuggingFace" : "OpenAI"}
                  </Badge>
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
    </Container>
    {/* Dialog for adding a new embedding model */}
        <Dialog.Root open={isOpen} onOpenChange={(details) => setIsOpen(details.open)}>
          <Dialog.Backdrop />
          <Dialog.Positioner>
          <Dialog.Content size={{ base: "xs", md: "md" }} placement="center">
            <Box position="relative">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAddModel();
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
                          width: '100%',
                          padding: '0.5rem',
                          borderRadius: '0.375rem',
                          borderColor: '#E2E8F0',
                          fontSize: '1rem',
                          height: '2.5rem',                          
                        }}
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
                          disabled={!modelId.trim()}
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
                <Dialog.Footer gap={2}>
                  <Dialog.ActionTrigger asChild>
                    <Button variant="subtle" colorPalette="gray">
                      Cancel
                    </Button>
                  </Dialog.ActionTrigger>
                  <Button
                    colorPalette="blue"
                    type="submit"
                    isDisabled={!isModelValid}
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
    </>
  )
}