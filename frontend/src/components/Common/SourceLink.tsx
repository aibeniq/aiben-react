import { type FilesGetSourceContentResponse, FilesService } from "@/client"
import { useFileViewer } from "@/hooks/useFileViewer"
import useCustomToast from "@/hooks/useCustomToast"
import { Link, type LinkProps } from "@chakra-ui/react"
import { useState } from "react"
import FileViewerModal from "./FileViewerModal"
import { Tooltip } from "../ui/tooltip"

interface SourceLinkProps extends LinkProps {
  sourceId: string
  fileName: string
  useModal?: boolean
  truncateText?: boolean
  maxLength?: number
  highlightSnippet?: string // Text snippet to search for and highlight in the file
}

const SourceLink: React.FC<SourceLinkProps> = ({
  sourceId,
  fileName,
  useModal = false,
  truncateText = false,
  maxLength = 60,
  highlightSnippet,
  ...rest
}) => {
  // In Chakra UI v3, we need to manually manage this state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { viewFile, viewFileInModal, currentFile, isLoading, clearFile } = useFileViewer()
  const [isLoadingFile, setIsLoadingFile] = useState(false)
  const [convertedPdfFile, setConvertedPdfFile] = useState<FilesGetSourceContentResponse | null>(
    null,
  ) // For DOCX converted to PDF
  const { showErrorToast } = useCustomToast()

  const handleClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()

    console.log("SourceLink clicked:", { sourceId, fileName, useModal })
    console.log("File extension check:", {
      fileName,
      toLowerCase: fileName.toLowerCase(),
      endsWithDocx: fileName.toLowerCase().endsWith(".docx"),
      endsWithRtf: fileName.toLowerCase().endsWith(".rtf"),
    })
    setIsLoadingFile(true)

    try {
      // Check if the file is a DOCX or RTF
      const isDocx = fileName.toLowerCase().endsWith(".docx")
      const isRtf = fileName.toLowerCase().endsWith(".rtf")

      if (isDocx || isRtf) {
        const fileType = isDocx ? "DOCX" : "RTF"
        console.log(`${fileType} detected! Converting to PDF for viewing:`, fileName)

        let pdfBlob: Blob

        // If sourceId is empty/null, use filename-based conversion
        if (!sourceId || sourceId.trim() === "") {
          console.log("No sourceId provided, using filename-based conversion:", fileName)
          if (isDocx) {
            pdfBlob = (await FilesService.convertDocxToPdfByFilename({
              filename: fileName,
            })) as Blob
          } else {
            pdfBlob = (await FilesService.convertRtfToPdfByFilename({
              filename: fileName,
            })) as Blob
          }
          console.log("PDF conversion by filename successful, blob size:", pdfBlob.size)
        } else {
          console.log("Using sourceId-based conversion:", sourceId)
          // Use the appropriate conversion endpoint with sourceId
          if (isDocx) {
            pdfBlob = (await FilesService.convertDocxToPdf({ sourceId })) as Blob
          } else {
            pdfBlob = (await FilesService.convertRtfToPdf({ sourceId })) as Blob
          }
          console.log("PDF conversion successful, blob size:", pdfBlob.size)
        }

        // Verify blob is valid
        if (!pdfBlob || pdfBlob.size === 0) {
          throw new Error("PDF conversion resulted in empty or invalid blob")
        }

        // Convert PDF blob to base64 for modal viewing
        const pdfArrayBuffer = await pdfBlob.arrayBuffer()
        const pdfUint8Array = new Uint8Array(pdfArrayBuffer)

        // Use a more robust method for large files to avoid call stack issues
        let binary = ""
        const len = pdfUint8Array.byteLength
        for (let i = 0; i < len; i++) {
          binary += String.fromCharCode(pdfUint8Array[i])
        }
        const pdfBase64 = btoa(binary)

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
          base64Length: pdfBase64.length,
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

        // If no sourceId is available, try filename-based viewing for PDFs and TXT files
        if (
          (!sourceId || sourceId.trim() === "") &&
          (fileName.toLowerCase().endsWith(".pdf") || fileName.toLowerCase().endsWith(".txt"))
        ) {
          console.log("No sourceId provided for PDF/TXT, using filename-based viewing:", fileName)

          try {
            const response = await FilesService.getSourceContentByFilename({
              filename: fileName,
            })
            console.log("PDF/TXT file data received:", response)

            if (useModal) {
              setConvertedPdfFile(response)
              setIsModalOpen(true)
              console.log("Opened PDF/TXT in modal using filename")
            } else {
              // Create a blob URL for the PDF/TXT and open in new tab
              const byteCharacters = atob(response.data_base64)
              const byteNumbers = new Array(byteCharacters.length)

              for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i)
              }

              const byteArray = new Uint8Array(byteNumbers)
              const blob = new Blob([byteArray], {
                type: response.content_type,
              })
              const url = URL.createObjectURL(blob)

              window.open(url, "_blank")
              console.log("Opened PDF/TXT in new tab using filename")
            }
          } catch (filenameError) {
            console.error("Filename-based PDF/TXT viewing failed:", filenameError)
            throw filenameError // Re-throw to trigger fallback
          }
        } else {
          // Use normal sourceId-based viewing
          // For .txt files, if sourceId method fails, try filename-based viewing as fallback
          const isTxtFile = fileName.toLowerCase().endsWith(".txt")

          try {
            if (useModal) {
              await viewFileInModal(sourceId)
              setIsModalOpen(true)
            } else {
              await viewFile(sourceId)
            }
          } catch (sourceIdError) {
            console.error("SourceId-based viewing failed:", sourceIdError)

            // For .txt files, try filename-based viewing as fallback
            if (isTxtFile) {
              console.log("Attempting filename-based fallback for .txt file:", fileName)
              try {
                const response = await FilesService.getSourceContentByFilename({
                  filename: fileName,
                })
                console.log("TXT file data received via filename fallback:", response)

                if (useModal) {
                  setConvertedPdfFile(response)
                  setIsModalOpen(true)
                  console.log("Opened TXT in modal using filename fallback")
                } else {
                  // Create a blob URL for the TXT and open in new tab
                  const byteCharacters = atob(response.data_base64)
                  const byteNumbers = new Array(byteCharacters.length)

                  for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i)
                  }

                  const byteArray = new Uint8Array(byteNumbers)
                  const blob = new Blob([byteArray], {
                    type: response.content_type,
                  })
                  const url = URL.createObjectURL(blob)

                  window.open(url, "_blank")
                  console.log("Opened TXT in new tab using filename fallback")
                }
              } catch (filenameError) {
                console.error("Filename-based TXT viewing also failed:", filenameError)
                throw sourceIdError // Re-throw the original error
              }
            } else {
              throw sourceIdError // Re-throw for non-txt files
            }
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

      // Check if this was a DOCX or RTF file that failed conversion
      const isDocx = fileName.toLowerCase().endsWith(".docx")
      const isRtf = fileName.toLowerCase().endsWith(".rtf")

      if (isDocx || isRtf) {
        const fileType = isDocx ? "DOCX" : "RTF"
        // For DOCX/RTF files, don't fall back to original method since they can't be displayed natively
        console.error(`${fileType} to PDF conversion failed, not attempting fallback`)
        showErrorToast(
          `Failed to convert ${fileType} file "${fileName}" to PDF for viewing. Please try again or download the file directly.`,
        )
      } else {
        // Fallback to original method if conversion fails for non-DOCX/RTF files
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

  console.log("Current file state:", {
    currentFile,
    convertedPdfFile,
    isLoading,
    isModalOpen,
  })

  // Helper function to truncate text with ellipsis
  const truncateFileName = (text: string): string => {
    if (!truncateText || text.length <= maxLength) return text
    return text.substring(0, maxLength) + "..."
  }

  // Determine which file to show in modal - converted PDF takes precedence
  const fileToShow = convertedPdfFile || currentFile
  const displayName = isLoadingFile ? "Loading..." : truncateFileName(fileName)
  const needsTooltip = truncateText && fileName.length > maxLength

  return (
    <>
      {needsTooltip ? (
        <Tooltip content={fileName} showArrow>
          <Link
            color="blue.500"
            _hover={{ textDecoration: "underline" }}
            onClick={handleClick}
            {...rest}
          >
            {displayName}
          </Link>
        </Tooltip>
      ) : (
        <Link
          color="blue.500"
          _hover={{ textDecoration: "underline" }}
          onClick={handleClick}
          {...rest}
        >
          {displayName}
        </Link>
      )}

      {useModal && fileToShow && (
        <FileViewerModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          file={fileToShow}
          isLoading={isLoading}
          highlightSnippet={highlightSnippet}
        />
      )}
    </>
  )
}

export default SourceLink
