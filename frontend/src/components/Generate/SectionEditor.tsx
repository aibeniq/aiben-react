import React, { useState, useEffect, useRef } from "react"
import { VStack, HStack, Input, Text, Switch, IconButton, Box } from "@chakra-ui/react"
import { FiTrash2, FiChevronUp, FiChevronDown } from "react-icons/fi"
import { generateUUID } from "../../utils/uuid"

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
              id: item.id || generateUUID(),
              text: item.text,
              consultDocuments: item.consultDocuments,
            }))
            // Ensure there's always an empty section at the end
            if (items.length === 0 || items[items.length - 1].text.trim() !== "") {
              items.push({ id: generateUUID(), text: "", consultDocuments: true })
            }
            setSectionItems(items)
          } else {
            throw new Error("Not structured format")
          }
        } catch {
          const items = sections
            .split("\n")
            .filter((line) => line.trim())
            .map((text) => ({
              id: generateUUID(),
              text: text.trim(),
              consultDocuments: true,
            }))
          // Ensure there's always an empty section at the end
          items.push({ id: generateUUID(), text: "", consultDocuments: true })
          setSectionItems(items)
        }
      } else {
        // Start with one empty section
        setSectionItems([{ id: generateUUID(), text: "", consultDocuments: true }])
      }
      lastSectionsValueRef.current = sections
    }
  }, [sections])

  // Initialize with empty section if starting fresh
  useEffect(() => {
    if (sectionItems.length === 0) {
      setSectionItems([{ id: generateUUID(), text: "", consultDocuments: true }])
    }
  }, [])

  const handleSectionChange = (id: string, field: keyof SectionItem, value: any) => {
    setSectionItems((currentItems) => {
      const updatedItems = currentItems.map((item) =>
        item.id === id ? { ...item, [field]: value } : item,
      )

      // If we're updating text and this is the last item and it's not empty anymore,
      // add a new empty section at the end
      if (field === "text" && value.trim() !== "") {
        const itemIndex = currentItems.findIndex((item) => item.id === id)
        if (itemIndex === currentItems.length - 1) {
          updatedItems.push({ id: generateUUID(), text: "", consultDocuments: true })
        }
      }

      return updatedItems
    })
  }

  const removeSection = (id: string) => {
    setSectionItems((currentItems) => {
      const updated = currentItems.filter((item) => item.id !== id)
      // Ensure we always have at least one empty section
      if (updated.length === 0 || updated[updated.length - 1].text.trim() !== "") {
        updated.push({ id: generateUUID(), text: "", consultDocuments: true })
      }
      return updated
    })
  }

  const moveSectionUp = (index: number) => {
    if (index === 0) return
    setSectionItems((currentItems) => {
      const newItems = [...currentItems]
      ;[newItems[index - 1], newItems[index]] = [newItems[index], newItems[index - 1]]
      return newItems
    })
  }

  const moveSectionDown = (index: number) => {
    setSectionItems((currentItems) => {
      if (index === currentItems.length - 1) return currentItems
      const newItems = [...currentItems]
      ;[newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]]
      return newItems
    })
  }

  useEffect(() => {
    console.log("SectionEditor: sectionItems changed, notifying parent", sectionItems)
    // Filter out empty sections for the parent (except keep one empty for editing)
    const nonEmptySections = sectionItems.filter((item) => item.text.trim() !== "")

    const structuredData = nonEmptySections.map((item) => ({
      id: item.id,
      text: item.text,
      consultDocuments: item.consultDocuments,
    }))
    const sectionsString = JSON.stringify(structuredData)
    lastSectionsValueRef.current = sectionsString // Prevent re-parsing our own changes
    callbacks.current.onSectionsChange(sectionsString)
    if (callbacks.current.onStructuredSectionsChange) {
      callbacks.current.onStructuredSectionsChange(nonEmptySections)
    }
  }, [sectionItems])

  return (
    <VStack gap={0} align="stretch" w="full">
      <VStack
        align="stretch"
        gap={0}
        overflowY="auto"
        maxH="300px"
        css={{
          "&:after": {
            content: '""',
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "25px",
            background: "linear-gradient(to top, white, transparent)",
            pointerEvents: "none",
          },
        }}
      >
        {sectionItems.map((item, index) => {
          const isLastEmptySection = index === sectionItems.length - 1 && item.text.trim() === ""
          const canRemove = sectionItems.length > 1 && item.text.trim() !== ""

          return (
            <div
              key={item.id}
              style={{
                position: "relative",
                display: "flex",
                paddingTop: "0.25rem",
                paddingBottom: "0.25rem",
                borderRadius: "0.375rem",
                backgroundColor: "transparent",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <HStack gap={3} align="center" w="full">
                {!isLastEmptySection && (
                  <Switch.Root
                    ids={{
                      root: `switch-root-${item.id}`,
                      hiddenInput: `switch-input-${item.id}`,
                    }}
                    checked={item.consultDocuments}
                    onCheckedChange={(details) => {
                      handleSectionChange(item.id, "consultDocuments", details.checked)
                    }}
                    size="sm"
                    colorPalette="teal"
                  >
                    <Switch.HiddenInput />
                    <Switch.Control />
                    <Switch.Label>
                      <Text fontSize="xs">Consult docs</Text>
                    </Switch.Label>
                  </Switch.Root>
                )}

                <div style={{ flex: "1", width: "100%" }}>
                  <Input
                    value={item.text}
                    onChange={(e) => handleSectionChange(item.id, "text", e.target.value)}
                    placeholder={isLastEmptySection ? "Add section" : "Section description"}
                    size="sm"
                    borderTop="none"
                    borderLeft="none"
                    borderRight="none"
                    borderBottom="1px solid"
                    borderColor="gray.200"
                    borderRadius="none"
                    bg="transparent"
                    px={2}
                    py={0}
                    w="full"
                    _focus={{
                      borderTop: "none",
                      borderLeft: "none",
                      borderRight: "none",
                      borderBottom: "1px solid",
                      borderColor: "blue.300",
                      boxShadow: "none",
                      outline: "none",
                      bg: "transparent",
                    }}
                    _placeholder={{
                      color: isLastEmptySection ? "gray.400" : "gray.500",
                      fontStyle: isLastEmptySection ? "italic" : "normal",
                    }}
                  />
                </div>

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
                  {canRemove && (
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
                  )}
                </Box>
              </HStack>
            </div>
          )
        })}
      </VStack>
    </VStack>
  )
}

export default SectionEditor
