import type { SourceContentResponse } from "@/client"
import { Box, Button, Dialog, Image, Spinner, Text } from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { cleanRTFFormatting } from "../../utils/rtfCleaner"

interface FileViewerModalProps {
  file: SourceContentResponse | File | null
  isOpen: boolean
  isLoading: boolean
  onClose: () => void
  highlightSnippet?: string // Text snippet to search for and highlight
}

const FileViewerModal: React.FC<FileViewerModalProps> = ({
  file,
  isOpen,
  isLoading,
  onClose,
  highlightSnippet,
}) => {
  const [fileUrl, setFileUrl] = useState<string | null>(null)
  const [textContent, setTextContent] = useState<string | null>(null)
  const textContentRef = useRef<HTMLDivElement>(null)

  // Helper function to progressively search for text with resilient matching
  const findBestMatch = (
    text: string,
    originalSnippet: string,
  ): { regex: RegExp; parts: string[]; matchedText: string } | null => {
    const normalizedText = text.replace(/\s+/g, " ").trim()

    // Function to normalize text for comparison
    const normalizeForSearch = (str: string) => {
      return str
        .replace(/\s+/g, " ") // Normalize whitespace
        .replace(/[-–—]/g, "-") // Normalize dashes
        .replace(/[""]/g, '"') // Normalize quotes
        .replace(/['']/g, "'") // Normalize apostrophes
        .replace(/\n/g, " ") // Replace newlines with spaces
        .trim()
    }

    let searchText = normalizeForSearch(originalSnippet)
    
    // Limit search text length to prevent regex recursion issues (similar to PDF limit)
    const maxTextSearchLength = 1000  // Reasonable limit for text files (adjust as needed)
    if (searchText.length > maxTextSearchLength) {
      // Trim to word boundary
      const trimmed = searchText.substring(0, maxTextSearchLength)
      const lastSpace = trimmed.lastIndexOf(" ")
      if (lastSpace > maxTextSearchLength * 0.7) {
        searchText = trimmed.substring(0, lastSpace)
      } else {
        searchText = trimmed
      }
    }

    const minLength = Math.max(15, Math.min(50, searchText.length * 0.3)) // At least 15 chars or 30% of original

    console.log(
      "Starting progressive search with:",
      searchText.substring(0, 50),
    )
    console.log("Minimum search length:", minLength)

    // Try progressively shorter versions of the text
    while (searchText.length >= minLength) {
      console.log(
        `Trying search with length ${searchText.length}:`,
        searchText.substring(0, 30),
      )

      try {
        // Try exact match first
        let regex = new RegExp(
          `(${searchText.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
          "gi",
        )
        let parts = normalizedText.split(regex)

        if (parts.length > 1) {
          console.log("✅ Found exact match at length:", searchText.length)
          return { regex, parts, matchedText: searchText }
        }

        // Try fuzzy match - use more restrictive whitespace pattern to avoid backtracking
        const fuzzyPattern = searchText
          .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
          .replace(/\s+/g, "\\s{0,3}") // Limit to 0-3 spaces instead of unlimited

        regex = new RegExp(`(${fuzzyPattern})`, "gi")
        parts = normalizedText.split(regex)

        if (parts.length > 1) {
          console.log("✅ Found fuzzy match at length:", searchText.length)
          return { regex, parts, matchedText: searchText }
        }

        // Try word-boundary based search for better matching
        if (searchText.split(" ").length > 1) {
          const wordBoundaryPattern = searchText
            .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
            .replace(/\s+/g, "\\s+") // Require at least one whitespace

          regex = new RegExp(`\\b(${wordBoundaryPattern})\\b`, "gi")
          parts = normalizedText.split(regex)

          if (parts.length > 1) {
            console.log(
              "✅ Found word-boundary match at length:",
              searchText.length,
            )
            return { regex, parts, matchedText: searchText }
          }
        }
      } catch (error) {
        console.warn(
          "Error with regex at length",
          searchText.length,
          ":",
          error,
        )
      }

      // Trim from the end - remove last word or last 10% of characters, whichever is smaller
      const words = searchText.split(" ")
      if (words.length > 1) {
        // Remove last word
        searchText = words.slice(0, -1).join(" ").trim()
      } else {
        // Remove last 10% of characters, but at least 1 character
        const charsToRemove = Math.max(1, Math.floor(searchText.length * 0.1))
        searchText = searchText
          .substring(0, searchText.length - charsToRemove)
          .trim()
      }
    }

    console.log("❌ No match found even with minimum length")
    return null
  }

  // Helper function to highlight text and return JSX
  const highlightText = (text: string, snippet: string) => {
    if (!snippet || snippet.trim() === "") {
      console.log("No snippet provided for highlighting")
      return text
    }

    console.log("🔍 Starting resilient text highlighting")
    console.log("Original snippet:", snippet.substring(0, 100))
    console.log("Text length:", text.length)

    // Use the progressive search function
    const match = findBestMatch(text, snippet)

    if (!match) {
      console.warn(
        "❌ No matches found for any version of snippet:",
        snippet.substring(0, 50),
      )
      // Final fallback - try to match just the first few significant words
      const words = snippet.split(/\s+/).filter((word) => word.length > 3)
      if (words.length > 0) {
        const fallbackText = words.slice(0, 3).join(" ")
        console.log(
          "🔄 Trying fallback with first significant words:",
          fallbackText,
        )
        const fallbackMatch = findBestMatch(text, fallbackText)
        if (fallbackMatch) {
          console.log("✅ Fallback match found!")
          return createHighlightedContent(
            fallbackMatch.parts,
            fallbackMatch.regex,
          )
        }
      }
      return text
    }

    console.log("✅ Match found! Creating highlighted content")
    return createHighlightedContent(match.parts, match.regex)
  }

  // Helper function to create highlighted content
  const createHighlightedContent = (parts: string[], regex: RegExp) => {
    let firstHighlightFound = false

    return parts.map((part, index) => {
      // Check if this part matches our search term
      if (part?.trim() && regex.test(part)) {
        const isFirstMatch = !firstHighlightFound
        if (isFirstMatch) {
          firstHighlightFound = true
          console.log("✨ Creating first highlight element")
        }

        return (
          <span
            key={index}
            style={{
              backgroundColor: "#ffff00",
              fontWeight: "bold",
              padding: "2px 4px",
              borderRadius: "3px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              border: "1px solid #ffd700",
            }}
            id={isFirstMatch ? "first-highlight" : undefined}
            data-highlight="true"
          >
            {part}
          </span>
        )
      }
      return part
    })
  }

  // Helper function to get content type from either file type
  const getContentType = (file: SourceContentResponse | File): string => {
    return file instanceof File ? file.type : file.content_type
  }

  // Helper function to get file name from either file type
  const getFileName = (file: SourceContentResponse | File): string => {
    return file instanceof File ? file.name : file.name
  }

  // Function to scroll to the first highlighted text
  const scrollToHighlight = () => {
    if (!highlightSnippet) return

    // For text files, scroll to highlighted element
    if (textContentRef.current) {
      setTimeout(() => {
        const firstHighlight =
          textContentRef.current?.querySelector("#first-highlight")
        if (firstHighlight) {
          console.log("Found first highlight, scrolling to it")
          firstHighlight.scrollIntoView({
            behavior: "smooth",
            block: "center",
          })

          // Add a temporary glow effect to make it more noticeable
          const element = firstHighlight as HTMLElement
          element.style.boxShadow = "0 0 10px #ffff00, 0 0 20px #ffff00"
          setTimeout(() => {
            element.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)"
          }, 2000)
        } else {
          console.warn("No highlight element found to scroll to")
        }
      }, 200)
    }
  }

  useEffect(() => {
    if (!file) {
      setFileUrl(null)
      setTextContent(null)
      return
    }

    // Create a blob URL for the file
    const createBlobUrl = async () => {
      try {
        let byteArray: Uint8Array
        let contentType: string

        if (file instanceof File) {
          // Handle direct File object (for uploaded files)
          const arrayBuffer = await file.arrayBuffer()
          byteArray = new Uint8Array(arrayBuffer)
          contentType = file.type

          // For text files, also store the text content
          if (contentType.startsWith("text/")) {
            const text = await file.text()
            setTextContent(text)
          }
        } else {
          // Existing logic for FilesGetSourceContentResponse (knowledge base files)
          const byteCharacters = atob(file.data_base64)
          const byteNumbers = new Array(byteCharacters.length)
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i)
          }
          byteArray = new Uint8Array(byteNumbers)
          contentType = getContentType(file)

          // For text files, also store the text content
          if (contentType.startsWith("text/")) {
            setTextContent(atob(file.data_base64))
          }
        }

        const blob = new Blob([byteArray as any], { type: contentType })
        const url = URL.createObjectURL(blob)
        setFileUrl(url)
        console.log("Created file URL:", url)

        // Clean up when component unmounts
        return () => {
          if (url) URL.revokeObjectURL(url)
        }
      } catch (error) {
        console.error("Error creating blob URL:", error)
        setFileUrl(null)
        setTextContent(null)
      }
    }

    createBlobUrl()
  }, [file])

  // Scroll to highlighted text when modal opens and file is loaded
  useEffect(() => {
    if (isOpen && file && highlightSnippet) {
      console.log(
        "Modal opened with highlight snippet:",
        highlightSnippet.substring(0, 50),
      )

      // For text files, try scrolling multiple times to ensure it works
      if (getContentType(file).startsWith("text/")) {
        scrollToHighlight()
        // Try again after a longer delay in case the content takes time to render
        setTimeout(scrollToHighlight, 500)
        setTimeout(scrollToHighlight, 1000)
      }
    }
  }, [isOpen, file, highlightSnippet])

  // Helper function to create the best PDF search text
  const createPdfSearchText = (snippet: string): string => {
    if (!snippet || snippet.trim() === "") return ""

    // Normalize the snippet for PDF search
    let searchText = snippet
      .replace(/\s+/g, " ") // Normalize whitespace
      .replace(/[-–—]/g, "-") // Normalize dashes
      .replace(/[""]/g, '"') // Normalize quotes
      .replace(/['']/g, "'") // Normalize apostrophes
      .trim()

    // Start with a reasonable length for PDF search
    const maxPdfSearchLength = 80
    if (searchText.length > maxPdfSearchLength) {
      // Trim to word boundary
      const trimmed = searchText.substring(0, maxPdfSearchLength)
      const lastSpace = trimmed.lastIndexOf(" ")
      if (lastSpace > maxPdfSearchLength * 0.7) {
        searchText = trimmed.substring(0, lastSpace)
      } else {
        searchText = trimmed
      }
    }

    console.log("PDF search text created:", searchText)
    return searchText
  }

  const downloadFile = () => {
    if (!fileUrl || !file) return

    const a = document.createElement("a")
    a.href = fileUrl
    a.download = file.name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const renderFileContent = () => {
    if (!fileUrl || !file) return null

    // Images
    if (getContentType(file).startsWith("image/")) {
      return <Image src={fileUrl} alt={file.name} maxH="70vh" />
    }

    // PDF
    if (getContentType(file) === "application/pdf") {
      // For PDFs, we'll use progressive search strategy
      let pdfUrl = fileUrl

      if (highlightSnippet && fileUrl) {
        // Use the improved PDF search text function
        const searchText = createPdfSearchText(highlightSnippet)
        const encodedSearch = encodeURIComponent(searchText)

        // PDF.js supports search parameter with phrase matching
        pdfUrl = `${fileUrl}#search=${encodedSearch}&phrase=true`

        console.log("🎯 PDF URL with progressive search:", pdfUrl)
        console.log("🔍 Optimized search text:", searchText)
      }

      return (
        <Box>
          <Box h="70vh" w="100%" position="relative">
            <iframe
              src={pdfUrl}
              style={{ width: "100%", height: "100%", border: "none" }}
              title={file.name}
              onLoad={() => {
                console.log("PDF iframe loaded")
                if (highlightSnippet) {
                  const searchText = createPdfSearchText(highlightSnippet)
                  console.log(
                    "PDF loaded with optimized search snippet:",
                    searchText,
                  )

                  // Try to send search command to PDF.js after load
                  setTimeout(() => {
                    try {
                      const iframe = document.querySelector(
                        `iframe[title="${file.name}"]`,
                      ) as HTMLIFrameElement
                      if (iframe?.contentWindow) {
                        // Attempt to trigger search in PDF.js with optimized text
                        iframe.contentWindow.postMessage(
                          {
                            type: "search",
                            text: searchText,
                          },
                          "*",
                        )
                        console.log("📤 Sent PDF search message:", searchText)
                      }
                    } catch (e) {
                      console.log(
                        "Could not send search message to PDF iframe:",
                        e,
                      )
                    }
                  }, 1000)
                }
              }}
            />
          </Box>
        </Box>
      )
    }

    // Plain text
    if (getContentType(file).startsWith("text/")) {
      // Use the text content loaded in useEffect
      const displayTextContent = textContent || ""

      // Check if this is an RTF file and clean the formatting
      const isRtfFile =
        getFileName(file).toLowerCase().endsWith(".rtf") ||
        getContentType(file).includes("rtf") ||
        displayTextContent.startsWith("{\\rtf")

      const displayContent = isRtfFile
        ? cleanRTFFormatting(displayTextContent)
        : displayTextContent

      return (
        <Box
          ref={textContentRef}
          as="div"
          maxH="70vh"
          overflow="auto"
          p={4}
          bg="surface"
          borderRadius="md"
          fontSize="sm"
          whiteSpace="pre-wrap"
          style={{ fontFamily: "monospace" }}
        >
          {highlightSnippet
            ? highlightText(displayContent, highlightSnippet)
            : displayContent}
        </Box>
      )
    }

    // Default case
    return (
      <Box textAlign="center" py={8}>
        <Text mb={4}>
          Preview not available for this file type ({getContentType(file)})
        </Text>
        <Button onClick={downloadFile} colorPalette="blue">
          Download File
        </Button>
      </Box>
    )
  }

  console.log("Modal rendering with isOpen:", isOpen)

  return (
    <Dialog.Root
      open={isOpen}
      onOpenChange={({ open }) => !open && onClose()}
      size="xl"
    >
      <Dialog.Backdrop />
      <Dialog.Positioner>
        <Dialog.Content>
          <Dialog.Header>{file?.name || "View File"}</Dialog.Header>
          <Dialog.CloseTrigger />
          <Dialog.Body>
            {isLoading ? (
              <Box textAlign="center" py={10}>
                <Spinner size="lg" />
                <Text mt={4}>Loading file...</Text>
              </Box>
            ) : (
              renderFileContent()
            )}
          </Dialog.Body>
          <Dialog.Footer>
            <Button variant="outline" mr={3} onClick={onClose}>
              Close
            </Button>
            {file && (
              <Button
                colorPalette="blue"
                onClick={downloadFile}
                disabled={!fileUrl}
              >
                Download
              </Button>
            )}
          </Dialog.Footer>
        </Dialog.Content>
      </Dialog.Positioner>
    </Dialog.Root>
  )
}

export default FileViewerModal
