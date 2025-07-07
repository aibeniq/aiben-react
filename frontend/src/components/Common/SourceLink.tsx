import { Link, LinkProps } from "@chakra-ui/react"
import { useFileViewer } from "@/hooks/useFileViewer"
import FileViewerModal from "./FileViewerModal"
import { useState } from "react"

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

  const handleClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()

    console.log("SourceLink clicked:", { sourceId, fileName, useModal })
    setIsLoadingFile(true)

    if (useModal) {
      try {
        await viewFileInModal(sourceId)
        // Only open modal after successfully fetching file
        setIsModalOpen(true)
      } catch (error) {
        console.error("Error loading file in modal:", error)
      }
    } else {
      try {
        await viewFile(sourceId)
      } catch (error) {
        console.error("Error loading file:", error)
      }
    }

    setIsLoadingFile(false)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    clearFile()
  }

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

      {useModal && currentFile && (
        <FileViewerModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          file={currentFile}
          isLoading={isLoading}
        />
      )}
    </>
  )
}

export default SourceLink
