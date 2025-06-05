import { useState } from "react"
import { FilesService } from "@/client"
import useCustomToast from "./useCustomToast"

export interface FileViewData {
  id: string
  name: string
  data_base64: string
  content_type: string
}

export const useFileViewer = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [currentFile, setCurrentFile] = useState<FileViewData | null>(null)
  const { showErrorToast } = useCustomToast()

  /**
   * Opens a file viewer for a source ID
   */
  const viewFile = async (sourceId: string) => {
    if (!sourceId) {
      showErrorToast("Invalid source ID")
      return
    }

    setIsLoading(true)
    console.log(`Fetching file with source ID: ${sourceId}`)

    try {
      // Fetch the file data from the API
      const response = await FilesService.getSourceContent({ sourceId })
      console.log("File data received:", response)
      setCurrentFile(response as FileViewData)

      // Create a blob URL for the file
      // @ts-expect-error TS2339
      const byteCharacters = atob(response.data_base64)
      const byteNumbers = new Array(byteCharacters.length)

      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }

      const byteArray = new Uint8Array(byteNumbers)
      // @ts-expect-error TS2339
      const blob = new Blob([byteArray], { type: response.content_type })
      const url = URL.createObjectURL(blob)

      // Open the file in a new tab
      window.open(url, "_blank")
    } catch (error) {
      console.error("Error viewing file:", error)
      showErrorToast("Failed to open file for viewing")
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Alternative that opens a modal instead of a new tab
   * Useful if you want to keep users in the application
   */
  const viewFileInModal = async (sourceId: string) => {
    if (!sourceId) {
      showErrorToast("Invalid source ID")
      return
    }

    setIsLoading(true)
    console.log(`Fetching file for modal with source ID: ${sourceId}`)
    try {
      // Fetch the file data from the API
      const response = await FilesService.getSourceContent({ sourceId })
      console.log("File data received for modal:", response)
      // @ts-expect-error TS2345
      setCurrentFile(response)
    } catch (error) {
      console.error("Error viewing file:", error)
      showErrorToast("Failed to open file for viewing")
      setCurrentFile(null)
    } finally {
      setIsLoading(false)
    }
  }

  const clearFile = () => {
    setCurrentFile(null)
  }

  return {
    viewFile,
    viewFileInModal,
    clearFile,
    currentFile,
    isLoading,
  }
}
