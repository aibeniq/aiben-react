import { Link, LinkProps } from "@chakra-ui/react"
import { useFileViewer } from "@/hooks/useFileViewer"
import FileViewerModal from "./FileViewerModal"
import { useState } from "react"
import { FilesService, FilesGetSourceContentResponse } from "@/client"

interface SourceLinkProps extends LinkProps {
  sourceId: string
  fileName: string
  useModal?: boolean
}

const SourceLink: React.FC<SourceLinkProps> = ({
  sourceId,
  fileName,
  useModal = false,
  ...rest
}) => {
  // In Chakra UI v3, we need to manually manage this state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { viewFile, viewFileInModal, currentFile, isLoading, clearFile } = useFileViewer()
  const [isLoadingFile, setIsLoadingFile] = useState(false)
  const [convertedPdfFile, setConvertedPdfFile] = useState<FilesGetSourceContentResponse | null>(
    null,
  ) // For DOCX converted to PDF

  const handleClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()

    console.log("SourceLink clicked:", { sourceId, fileName, useModal })
    console.log("File extension check:", {
      fileName,
      toLowerCase: fileName.toLowerCase(),
      endsWithDocx: fileName.toLowerCase().endsWith(".docx"),
    })
    setIsLoadingFile(true)

    try {
      // Check if the file is a DOCX
      const isDocx = fileName.toLowerCase().endsWith(".docx")

      if (isDocx) {
        console.log("DOCX detected! Converting to PDF for viewing:", fileName)

        let pdfBlob: Blob

        // If sourceId is empty/null, use filename-based conversion
        if (!sourceId || sourceId.trim() === "") {
          console.log("No sourceId provided, using filename-based conversion:", fileName)
          pdfBlob = (await FilesService.convertDocxToPdfByFilename({ filename: fileName })) as Blob
          console.log("PDF conversion by filename successful, blob size:", pdfBlob.size)
        } else {
          console.log("Using sourceId-based conversion:", sourceId)
          // Use the DOCX to PDF conversion endpoint with sourceId
          pdfBlob = (await FilesService.convertDocxToPdf({ sourceId })) as Blob
          console.log("PDF conversion successful, blob size:", pdfBlob.size)
        }

        // Convert PDF blob to base64 for modal viewing
        const pdfArrayBuffer = await pdfBlob.arrayBuffer()
        const pdfUint8Array = new Uint8Array(pdfArrayBuffer)
        const pdfBase64 = btoa(String.fromCharCode(...pdfUint8Array))

        // Create a fake response object compatible with FilesGetSourceContentResponse
        const pdfFilename = fileName.replace(/\.docx$/i, ".pdf")
        const fakeResponse = {
          id: sourceId || "converted-docx",
          name: pdfFilename,
          data_base64: pdfBase64,
          content_type: "application/pdf",
        }

        console.log("Created fake response for modal:", {
          name: fakeResponse.name,
          contentType: fakeResponse.content_type,
        })

        if (useModal) {
          // Set the converted PDF as current file for modal viewing
          setConvertedPdfFile(fakeResponse)
          setIsModalOpen(true)
          console.log("Opened converted PDF in modal")
        } else {
          // Fallback to new tab if modal not requested
          const blobUrl = URL.createObjectURL(pdfBlob)
          window.open(blobUrl, "_blank")
          console.log("Opened PDF in new tab")
        }
      } else {
        console.log("Non-DOCX file, using normal viewing method")
        // Handle non-DOCX files normally

        // If no sourceId is available, try filename-based viewing for PDFs
        if ((!sourceId || sourceId.trim() === "") && fileName.toLowerCase().endsWith(".pdf")) {
          console.log("No sourceId provided for PDF, using filename-based viewing:", fileName)

          try {
            const response = await FilesService.getSourceContentByFilename({ filename: fileName })
            console.log("PDF file data received:", response)

            if (useModal) {
              setConvertedPdfFile(response)
              setIsModalOpen(true)
              console.log("Opened PDF in modal using filename")
            } else {
              // Create a blob URL for the PDF and open in new tab
              const byteCharacters = atob(response.data_base64)
              const byteNumbers = new Array(byteCharacters.length)

              for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i)
              }

              const byteArray = new Uint8Array(byteNumbers)
              const blob = new Blob([byteArray], { type: response.content_type })
              const url = URL.createObjectURL(blob)

              window.open(url, "_blank")
              console.log("Opened PDF in new tab using filename")
            }
          } catch (filenameError) {
            console.error("Filename-based PDF viewing failed:", filenameError)
            throw filenameError // Re-throw to trigger fallback
          }
        } else {
          // Use normal sourceId-based viewing
          if (useModal) {
            await viewFileInModal(sourceId)
            setIsModalOpen(true)
          } else {
            await viewFile(sourceId)
          }
        }
      }
    } catch (error) {
      console.error("Error loading document:", error)
      console.error("Error details:", {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        name: error instanceof Error ? error.name : typeof error,
      })

      // Fallback to original method if conversion fails
      console.log("Attempting fallback to original viewing method")
      try {
        if (useModal) {
          await viewFileInModal(sourceId)
          setIsModalOpen(true)
        } else {
          await viewFile(sourceId)
        }
        console.log("Fallback method succeeded")
      } catch (fallbackError) {
        console.error("Fallback method also failed:", fallbackError)
      }
    } finally {
      setIsLoadingFile(false)
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    clearFile()
    setConvertedPdfFile(null) // Clear converted PDF file as well
  }

  console.log("Current file state:", { currentFile, convertedPdfFile, isLoading, isModalOpen })

  // Determine which file to show in modal - converted PDF takes precedence
  const fileToShow = convertedPdfFile || currentFile

  return (
    <>
      <Link
        color="blue.500"
        _hover={{ textDecoration: "underline" }}
        onClick={handleClick}
        {...rest}
      >
        {isLoadingFile ? "Loading..." : fileName}
      </Link>

      {useModal && fileToShow && (
        <FileViewerModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          file={fileToShow}
          isLoading={isLoading}
        />
      )}
    </>
  )
}

export default SourceLink
