import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  Textarea,
  VStack,
  HStack,
  Spinner,
  Input,
  Separator,
  Table,
  Accordion,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import SourceLink from "@/components/Common/SourceLink"
import { useState, useEffect } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation, useQuery } from "@tanstack/react-query"
import { ReportgenieService, KnowledgeBasesService } from "@/client"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FiFileText, FiCopy, FiCheck, FiDownload } from "react-icons/fi"
import { Field } from "../../components/ui/field"

const ReportGenie = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyReport = async () => {
    try {
      await navigator.clipboard.writeText(generatedReport);
      setCopySuccess(true);
      
      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false);
      }, 2000);
      
      showSuccessToast("Report copied to clipboard");
    } catch (err) {
      console.error("Failed to copy report:", err);
      showErrorToast("Failed to copy report to clipboard");
    }
  };

  const handleDownloadReport = async () => {
    try {
      setLoadingDownload(true);

      const response = await ReportgenieService.generateDocx({ requestBody: { content: generatedReport } });
      console.log("typeof response:", typeof response);
      console.log("response instanceof Blob:", response instanceof Blob);
      console.log("response:", response);

      let blob;
      if (response instanceof Blob) {
        console.log("Response is a Blob");
        blob = response;
      } else if (response instanceof ArrayBuffer) {
        console.log("Response is an ArrayBuffer");
        blob = new Blob([response], {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        });
      } else {
        console.log("Response is a string or unexpected type");
        // If response is a string (shouldn't be, but fallback)
        blob = new Blob([response], {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        });
      }

      /*
      console.log("Now attempting direct API call")
      const res = await fetch('/api/v1/reportgenie/generate/docx', {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: generatedReport })
      });
      const blob2= await res.blob();
      */

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      a.href = url;
      a.download = `report_${timestamp}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showSuccessToast("Report downloaded successfully");
    } catch (err) {
      console.error("Failed to download report:", err);
      showErrorToast(`Failed to download report: ${err.message || "Unknown error"}`);
    } finally {
      setLoadingDownload(false);
    }
  };

  const [loadingDownload, setLoadingDownload] = useState(false);

  const fetchOutlines = async () => {
    try {
      console.log("Fetching outlines...");
      const data = await ReportgenieService.getOutlines();
      console.log("Fetched outlines:", data);
      setOutlines(data || []);
    } catch (error) {
      console.error("Error fetching outlines:", error);
      showErrorToast("Failed to fetch outlines");
    }
  };

    // Call the function on component mount
  useEffect(() => {
    fetchOutlines();
  }, []);

  // Knowledge base selection state
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<any>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<any[]>([]);
  const [selectedKnowledgeBaseDetails, setSelectedKnowledgeBaseDetails] = useState<any>(null);
  
  // Outline content state
  const [sections, setSections] = useState("");
  const [outlines, setOutlines] = useState([]);
  const [selectedOutline, setSelectedOutline] = useState(null);
  const [outlineName, setOutlineName] = useState("");
  const [outlineDescription, setOutlineDescription] = useState("");

  // Results state
  const [generatedReport, setGeneratedReport] = useState("");
  const [sectionResults, setSectionResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedSection, setExpandedSection] = useState<number | null>(null);

  // Function to clean up filenames in source paths
  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown";
    
    if (source.includes('/tmp/') || source.includes('\\tmp\\')) {
      const filename = source.split('/').pop() || 
                      source.split('\\').pop() || '';
      
      return filename.includes('_') 
        ? filename.substring(filename.indexOf('_') + 1) 
        : filename;
    }
    
    return source;
  };

  // Fetch knowledge bases on component mount
  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        const response = await KnowledgeBasesService.readKnowledgeBases({ 
          skip: 0, 
          limit: 100
        });
        setKnowledgeBases(response.data || []);
      } catch (error) {
        console.error("Error fetching knowledge bases:", error);
        showErrorToast("Failed to fetch knowledge bases");
      }
    };

    fetchKnowledgeBases();
  }, []);

  // Fetch knowledge base details when a KB is selected
  const fetchKnowledgeBaseDetails = async (knowledgeBaseId: string) => {
    try {
      const response = await KnowledgeBasesService.readKnowledgeBase({ id: knowledgeBaseId });
      setSelectedKnowledgeBaseDetails(response);
    } catch (error) {
      console.error("Error fetching knowledge base details:", error);
      showErrorToast("Failed to fetch knowledge base details");
    }
  };

  // Mutation hook for generating the report
  const mutation = useMutation({
    mutationFn: (data: {
      sections: string;
      knowledgeBaseId: string;
    }) => {
      console.log("Now beginning report generation...")
      
      return ReportgenieService.generateReport({
        sections: data.sections,
        knowledgeBaseId: data.knowledgeBaseId,
      })
    },
    onSuccess: (data) => {
      console.log("Report generation successful:", data)
      
      setGeneratedReport(data.results.full_report);
      setSectionResults(data.results.sections || []);
    },
    onError: (error) => {
      console.log("Report generation failed:", error)
      showErrorToast(`Failed to generate report: ${error.message}`);
    },
  });

  // Query for fetching saved outlines
  const { data: outlineData, refetch: refetchOutlines } = useQuery({
    queryKey: ["reportOutlines"],
    queryFn: () => ReportgenieService.getOutlines(),
    onSuccess: (data) => {
      console.log("Fetched outlines:", data);
      setOutlines(data);
    },
    onError: (error) => {
      console.error("Failed to fetch outlines:", error);
      showErrorToast("Failed to fetch saved outlines");
    }
  });

  useEffect(() => {
    const fetchOutlines = async () => {
      try {
        console.log("Fetching outlines on component mount...");
        const response = await ReportgenieService.getOutlines();
        console.log("Outlines fetched:", response);
        setOutlines(response || []);
      } catch (error) {
        console.error("Error fetching outlines:", error);
        showErrorToast("Failed to fetch outlines");
      }
    };

    fetchOutlines();
  }, []); // Empty dependency array means this runs once on mount

  // Handle generating the report
  const handleGenerateReport = async () => {
    if (!sections.trim()) {
      showErrorToast("Please enter at least one section");
      return;
    }

    if (!selectedKnowledgeBase?.id) {
      showErrorToast("Please select a knowledge base");
      return;
    }

    const requestData = {
      sections: sections,
      knowledgeBaseId: selectedKnowledgeBase.id,
    };

    setLoading(true);
    mutation.mutate(requestData, {
      onSettled: () => {
        setLoading(false);
      },
    });
  };

  // Handle saving an outline
  const handleSaveOutline = async () => {
    if (!outlineName.trim()) {
      showErrorToast("Please enter a name for this outline");
      return;
    }

    if (!sections.trim()) {
      showErrorToast("Please enter at least one section");
      return;
    }

    try {
      if (selectedOutline) {
        // Update existing outline
        await ReportgenieService.updateOutline({
          outlineId: selectedOutline.id,
          requestBody: {
            name: outlineName,
            description: outlineDescription,
            sections: sections,
          },
        });
        showSuccessToast("Outline updated successfully");
      } else {
        // Create new outline
        const newOutline = await ReportgenieService.createOutline({
          requestBody: {
            name: outlineName,
            description: outlineDescription,
            sections: sections,
          },
        });
        showSuccessToast("Outline saved successfully");
      }
      
      // Reset form
      setSelectedOutline(null);
      setOutlineName("");
      setOutlineDescription("");
      
      // Fetch outlines after saving - this is the key change to match VeraDoc's approach
      await fetchOutlines();
    } catch (error) {
      console.error("Error saving outline:", error);
      showErrorToast(`Failed to save outline: ${error.message || "Unknown error"}`);
    }
  };

  // Custom components for markdown rendering
  const components = {
    table: (props) => (
      <Box as="table" width="full" borderWidth="1px" borderRadius="md" overflow="hidden" {...props} />
    ),
    thead: (props) => <Box as="thead" bg="gray.100" {...props} />,
    tbody: (props) => <Box as="tbody" {...props} />,
    tr: (props) => <Box as="tr" {...props} />,
    th: (props) => (
      <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
    ),
    td: (props) => (
      <Box as="td" p={4} borderBottomWidth="1px" {...props} />
    ),
  };

  return (
    <Container maxW="container.xl" py={8}>
      {/* Loading overlay */}
      {loading && (
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="rgba(255, 255, 255, 0.7)"
          zIndex="10"
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
        >
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text fontWeight="medium">Generating report...</Text>
          </VStack>
        </Box>
      )}

      <Heading size="xl" mb={6}>
        ReportGenie
      </Heading>
      
      <VStack spacing={6} align="stretch">
        {/* Knowledge Base Selection Section */}
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>Knowledge Base Selection</Heading>
          <Field label="Knowledge Bases" required>
            <select
              value={selectedKnowledgeBase?.id || ""}
              onChange={(e) => {
                const kb = knowledgeBases.find((kb) => kb.id === e.target.value);
                setSelectedKnowledgeBase(kb);
                if (kb?.id) {
                  fetchKnowledgeBaseDetails(kb.id);
                }
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                borderRadius: '0.375rem',
                borderColor: '#E2E8F0',
              }}
            >
              <option value="">Select a knowledge base</option>
              {knowledgeBases.map((kb) => (
                <option key={kb.id} value={kb.id}>
                  {kb.title}
                </option>
              ))}
            </select>
          </Field>

          {/* Knowledge base sources table */}
          {selectedKnowledgeBaseDetails?.files && selectedKnowledgeBaseDetails.files.length > 0 && (
            <Box mt={4}>
              <Text fontWeight="medium" mb={2}>Sources:</Text>
              <Table.Root variant="simple" size="sm">
                <Table.Header>
                  <Table.Row>
                    <Table.ColumnHeader>Name</Table.ColumnHeader>
                    <Table.ColumnHeader>Date Added</Table.ColumnHeader>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {selectedKnowledgeBaseDetails.files.map((file) => (
                    <Table.Row key={file.id}>
                      <Table.Cell>
                        <SourceLink
                          sourceId={file.id}
                          fileName={file.name}
                          useModal={true}
                          color="blue.600"
                          _hover={{ textDecoration: "underline" }}
                        />
                      </Table.Cell>
                      <Table.Cell>{new Date(file.date_created || '').toLocaleDateString()}</Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table.Root>
            </Box>
          )}
        </VStack>        

        <Separator my={4} />

        {/* Outline Selection and Management */}
        <VStack spacing={4} align="stretch">
          <Heading size="md" mb={2}>Report Outline</Heading>
          
          {/* Outline selection dropdown */}
          <Field label="Saved Outlines">
            <select
              value={selectedOutline?.id || ""}
              onChange={(e) => {
                const outline = outlines.find((o) => o.id === e.target.value);
                setSelectedOutline(outline);
                if (outline) {
                  setSections(outline.sections || "");
                  setOutlineName(outline.name || "");
                  setOutlineDescription(outline.description || "");
                }
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                borderRadius: '0.375rem',
                borderColor: '#E2E8F0',
              }}
            >
              <option value="">Select a saved outline</option>
              {outlines.map((outline) => (
                <option key={outline.id} value={outline.id}>
                  {outline.name}
                </option>
              ))}
            </select>
          </Field>

          {/* Outline name and description */}
          <Field label="Outline Name" required>
            <Input
              value={outlineName}
              onChange={(e) => setOutlineName(e.target.value)}
              placeholder="Enter outline name"
            />
          </Field>

          <Field label="Outline Description">
            <Textarea
              value={outlineDescription}
              onChange={(e) => setOutlineDescription(e.target.value)}
              placeholder="Enter outline description"
              resize="vertical"
            />
          </Field>

          {/* Sections input */}
          <Field label="Sections" required>
            <Textarea
              value={sections}
              onChange={(e) => setSections(e.target.value)}
              placeholder="Enter sections, one per line. Example:
CONTACT INFORMATION: Lists whom to contact with questions about the study, participant rights, or to report a research-related injury.
PURPOSE: Explains why the study is being done.
PROCEDURES: Describes what will happen during the research study."
              rows={8}
              resize="vertical"
            />
          </Field>

          {/* Buttons for outline management */}
          <HStack spacing={4} pt={2}>
            <Button
              variant="solid"
              onClick={handleSaveOutline}
            >
              {selectedOutline ? "Update Outline" : "Save Outline"}
            </Button>

            <Button
              variant="subtle"
              colorPalette="blue"
              onClick={async () => {
                if (!selectedOutline) {
                  showErrorToast("Please select an outline to copy");
                  return;
                }

                try {
                  await ReportgenieService.createOutline({
                    requestBody: {
                      name: `${selectedOutline.name} (Copy)`,
                      description: selectedOutline.description,
                      sections: selectedOutline.sections,
                    },
                  });
                  showSuccessToast("Outline copied successfully");
                  // Fetch outlines directly instead of using refetchOutlines
                  await fetchOutlines();
                } catch (error) {
                  console.error("Error copying outline:", error);
                  showErrorToast("Failed to copy outline");
                }
              }}
              isDisabled={!selectedOutline}
            >
              Copy Outline
            </Button>

            <Button
              variant="subtle"
              colorPalette="red"
              onClick={async () => {
                if (!selectedOutline) {
                  showErrorToast("Please select an outline to delete");
                  return;
                }

                try {
                  await ReportgenieService.deleteOutline({ outlineId: selectedOutline.id });
                  showSuccessToast("Outline deleted successfully");
                  setSelectedOutline(null);
                  setSections("");
                  setOutlineName("");
                  setOutlineDescription("");
                  // Fetch outlines directly instead of using refetchOutlines
                  await fetchOutlines();
                } catch (error) {
                  console.error("Error deleting outline:", error);
                  showErrorToast("Failed to delete outline");
                }
              }}
              isDisabled={!selectedOutline}
            >
              Delete Outline
            </Button>
          </HStack>
          
          {/* Generate Report Button */}
          <Button
            mt={4}
            variant="solid"
            colorPalette="green"
            size="lg"
            onClick={handleGenerateReport}
            isDisabled={!sections.trim() || !selectedKnowledgeBase?.id}
            isLoading={loading}
          >
            Generate Report
          </Button>
        </VStack>

        {/* Results Section */}
        {(generatedReport || sectionResults.length > 0) && (
          <>
            <Separator my={4} />
            <HStack justify="space-between" align="center" mb={4}>
            <Heading size="md">Generated Report</Heading>
            
            {/* Copy button */}
            {generatedReport && (
              <HStack spacing={2}>
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                  onClick={handleCopyReport}
                  colorPalette={copySuccess ? "green" : "blue"}
                >
                  {copySuccess ? "Copied!" : "Copy Report"}
                </Button>
                
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={<FiDownload />}
                  onClick={handleDownloadReport}
                  isLoading={loadingDownload}
                  loadingText="Downloading..."
                  colorPalette="green"
                >
                  Download DOCX
                </Button>
              </HStack>
            )}
          </HStack>
          
          <Box
            border="1px solid"
            borderColor="gray.200"
            borderRadius="md"
            p={4}
            bg="white"
            minH="100px"
            overflowY="auto"
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
              {generatedReport}
            </ReactMarkdown>

              {/* Detailed section results with sources */}
              {sectionResults.length > 0 && (
                <Box mt={8}>
                  <Heading as="h3" size="md" mb={4}>Sections with Sources</Heading>
                  
                  {sectionResults.map((section, index) => (
                    <Box 
                      key={index} 
                      mb={6} 
                      p={5} 
                      borderWidth="1px" 
                      borderRadius="md" 
                      bg={expandedSection === index ? "gray.50" : "white"}
                      _hover={{ bg: "gray.50" }}
                    >
                      <Heading as="h4" size="sm" mb={3} onClick={() => setExpandedSection(expandedSection === index ? null : index)} cursor="pointer">
                        Section {index + 1}: {section.title}
                      </Heading>
                      
                      {expandedSection === index && (
                        <>
                          <Box mb={4} p={3} borderLeft="4px solid" borderColor="blue.200">
                            <Text whiteSpace="pre-wrap">{section.content}</Text>
                          </Box>
                          
                          {section.source_citations && section.source_citations.length > 0 && (
                            <Accordion.Root type="single" collapsible mt={2}>
                              <Accordion.Item>
                                <Accordion.ItemTrigger bg="gray.100" _hover={{ bg: "gray.200" }}>
                                  <Box flex="1" textAlign="left" fontWeight="medium">
                                    <HStack>
                                      <FiFileText />
                                      <Text>View Source Citations ({section.source_citations.length})</Text>
                                    </HStack>
                                  </Box>
                                </Accordion.ItemTrigger>
                                <Accordion.ItemContent pb={4} bg="gray.50">
                                  {section.source_citations.map((citation, cIndex) => (
                                    <Box 
                                      key={cIndex}
                                      p={3} 
                                      mb={2} 
                                      borderWidth="1px" 
                                      borderRadius="md"
                                      bg="white"
                                    >
                                      {citation.metadata.source_data_id ? (
                                        <SourceLink
                                          sourceId={citation.metadata.source_data_id}
                                          fileName={getDisplayFileName(citation.metadata.source)}
                                          ml={1}
                                          fontWeight="normal"
                                          color="blue.600"
                                          useModal={true}
                                        />
                                      ) : (
                                        <Text as="span" ml={1} fontWeight="normal" color="blue.600">
                                          {getDisplayFileName(citation.metadata.source)}
                                        </Text>
                                      )}
                                      <Box 
                                        mt={2} 
                                        p={2} 
                                        bg="gray.50" 
                                        borderRadius="sm" 
                                        fontSize="sm"
                                        whiteSpace="pre-wrap"
                                      >
                                        {citation.content}
                                      </Box>
                                    </Box>
                                  ))}
                                </Accordion.ItemContent>
                              </Accordion.Item>
                            </Accordion.Root>
                          )}
                        </>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          </>
        )}
      </VStack>
    </Container>
  );
};

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/reportgenie")({
  component: ReportGenie,
});