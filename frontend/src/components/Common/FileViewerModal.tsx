import { Dialog, Box, Spinner, Text, Image, Button } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { type FileViewData } from "@/hooks/useFileViewer"

interface FileViewerModalProps {
  file: FileViewData | null
  isOpen: boolean
  isLoading: boolean
  onClose: () => void
}

const FileViewerModal: React.FC<FileViewerModalProps> = ({ file, isOpen, isLoading, onClose }) => {
  const [fileUrl, setFileUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!file) {
      setFileUrl(null)
      return
    }

    // Create a blob URL for the file
    try {
      const byteCharacters = atob(file.data_base64)
      const byteNumbers = new Array(byteCharacters.length)

      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }

      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: file.content_type })
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
    }
  }, [file])

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
    if (file.content_type.startsWith("image/")) {
      return <Image src={fileUrl} alt={file.name} maxH="70vh" />
    }

    // PDF
    if (file.content_type === "application/pdf") {
      return (
        <Box h="70vh" w="100%">
          <iframe
            src={fileUrl}
            style={{ width: "100%", height: "100%", border: "none" }}
            title={file.name}
          />
        </Box>
      )
    }

    // Plain text
    if (file.content_type.startsWith("text/")) {
      return (
        <Box
          as="pre"
          maxH="70vh"
          overflow="auto"
          p={4}
          bg="gray.50"
          borderRadius="md"
          fontSize="sm"
          whiteSpace="pre-wrap"
        >
          {atob(file.data_base64)}
        </Box>
      )
    }

    // Default case
    return (
      <Box textAlign="center" py={8}>
        <Text mb={4}>Preview not available for this file type ({file.content_type})</Text>
        <Button onClick={downloadFile} colorPalette="blue">
          Download File
        </Button>
      </Box>
    )
  }

  console.log("Modal rendering with isOpen:", isOpen)

  return (
    // @ts-expect-error TS2322
    <Dialog.Root open={isOpen} onOpenChange={({ open }) => !open && onClose()} size="5xl">
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
              // @ts-expect-error TS2322
              <Button colorPalette="blue" onClick={downloadFile} isDisabled={!fileUrl}>
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
