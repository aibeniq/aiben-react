import React, { useState, useEffect, useRef } from "react"
import { VStack, HStack, Input, Button, Text, Switch, IconButton, Box } from "@chakra-ui/react"
import { FiPlus, FiTrash2, FiChevronUp, FiChevronDown } from "react-icons/fi"

interface SectionItem {
  id: string
  text: string
  consultDocuments: boolean
}

interface SectionEditorProps {
  sections: string
  onSectionsChange: (sections: string) => void
  onStructuredSectionsChange?: (sections: SectionItem[]) => void
}

const SectionEditor: React.FC<SectionEditorProps> = ({
  sections,
  onSectionsChange,
  onStructuredSectionsChange,
}) => {
  const [sectionItems, setSectionItems] = useState<SectionItem[]>([])
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const lastSectionsValueRef = useRef<string>("")

  const callbacks = useRef({ onSectionsChange, onStructuredSectionsChange })
  useEffect(() => {
    callbacks.current = { onSectionsChange, onStructuredSectionsChange }
  }, [onSectionsChange, onStructuredSectionsChange])

  console.log("SectionEditor: sectionItems", sectionItems)

  // Only parse when sections prop changes from outside
  useEffect(() => {
    // Only update local state if the prop changed from outside (not from our own update)
    if (sections !== lastSectionsValueRef.current) {
      console.log("SectionEditor: sections prop changed from outside", sections)
      if (typeof sections === "string" && sections.trim()) {
        try {
          const parsedSections = JSON.parse(sections)
          if (
            Array.isArray(parsedSections) &&
            parsedSections.every(
              (item) => typeof item === "object" && "text" in item && "consultDocuments" in item,
            )
          ) {
            const items = parsedSections.map((item) => ({
              id: item.id || crypto.randomUUID(),
              text: item.text,
              consultDocuments: item.consultDocuments,
            }))
            setSectionItems(items)
          } else {
            throw new Error("Not structured format")
          }
        } catch {
          const items = sections
            .split("\n")
            .filter((line) => line.trim())
            .map((text) => ({
              id: crypto.randomUUID(),
              text: text.trim(),
              consultDocuments: true,
            }))
          setSectionItems(items)
        }
      } else {
        setSectionItems([])
      }
      lastSectionsValueRef.current = sections
    }
  }, [sections])

  const handleSectionChange = (id: string, field: keyof SectionItem, value: any) => {
    setSectionItems((currentItems) =>
      currentItems.map((item) => (item.id === id ? { ...item, [field]: value } : item)),
    )
  }

  const addSection = () => {
    const newItems = [
      ...sectionItems,
      { id: crypto.randomUUID(), text: "", consultDocuments: true },
    ]
    setSectionItems(newItems)
  }

  const removeSection = (id: string) => {
    const updated = sectionItems.filter((item) => item.id !== id)
    setSectionItems(updated)
  }

  const moveSectionUp = (index: number) => {
    if (index === 0) return
    const newItems = [...sectionItems]
    ;[newItems[index - 1], newItems[index]] = [newItems[index], newItems[index - 1]]
    setSectionItems(newItems)
  }

  const moveSectionDown = (index: number) => {
    if (index === sectionItems.length - 1) return
    const newItems = [...sectionItems]
    ;[newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]]
    setSectionItems(newItems)
  }

  useEffect(() => {
    console.log("SectionEditor: sectionItems changed, notifying parent", sectionItems)
    const structuredData = sectionItems.map((item) => ({
      id: item.id,
      text: item.text,
      consultDocuments: item.consultDocuments,
    }))
    const sectionsString = JSON.stringify(structuredData)
    lastSectionsValueRef.current = sectionsString // Prevent re-parsing our own changes
    callbacks.current.onSectionsChange(sectionsString)
    if (callbacks.current.onStructuredSectionsChange) {
      callbacks.current.onStructuredSectionsChange(sectionItems)
    }
  }, [sectionItems])

  return (
    <VStack gap={3} align="stretch" pr={2}>
      <Text fontSize="sm" fontWeight="medium" color="gray.700">
        Configure sections and document consultation:
      </Text>

      <VStack as="div" align="stretch" gap={3} overflowY="auto" maxH="300px">
        {sectionItems.map((item, index) => (
          <HStack
            key={item.id}
            gap={3}
            align="center"
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <Switch.Root
              ids={{
                root: `switch-root-${item.id}`,
                hiddenInput: `switch-input-${item.id}`,
              }}
              checked={item.consultDocuments}
              onCheckedChange={(details) => {
                handleSectionChange(item.id, "consultDocuments", details.checked)
              }}
              size="md"
              colorScheme="teal"
            >
              <Switch.HiddenInput />
              <Switch.Control />
              <Switch.Label>
                <Text fontSize="sm">Consult documents</Text>
              </Switch.Label>
            </Switch.Root>

            <Input
              value={item.text}
              onChange={(e) => handleSectionChange(item.id, "text", e.target.value)}
              placeholder="Section description"
              flex={1}
              size="sm"
            />

            <VStack gap={0} w="24px">
              <IconButton
                aria-label="Move section up"
                size="xs"
                variant="ghost"
                onClick={() => moveSectionUp(index)}
                disabled={index === 0}
                opacity={hoveredIndex === index && index > 0 ? 1 : 0}
              >
                <FiChevronUp size={12} />
              </IconButton>
              <IconButton
                aria-label="Move section down"
                size="xs"
                variant="ghost"
                onClick={() => moveSectionDown(index)}
                disabled={index === sectionItems.length - 1}
                opacity={hoveredIndex === index && index < sectionItems.length - 1 ? 1 : 0}
              >
                <FiChevronDown size={12} />
              </IconButton>
            </VStack>

            <Box w="32px" textAlign="center">
              <IconButton
                size="sm"
                variant="ghost"
                colorScheme="red"
                aria-label="Remove section"
                onClick={() => removeSection(item.id)}
                opacity={hoveredIndex === index ? 1 : 0}
              >
                <FiTrash2 />
              </IconButton>
            </Box>
          </HStack>
        ))}
      </VStack>

      <Button size="sm" onClick={addSection} variant="outline">
        <FiPlus />
        Add Section
      </Button>

      <Text fontSize="xs" color="gray.500">
        • Checked: Generate content using documents from knowledge base
        <br />• Unchecked: Use section text as-is in the report
      </Text>
    </VStack>
  )
}

export default SectionEditor
