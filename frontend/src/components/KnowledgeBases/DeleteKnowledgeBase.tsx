import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { FiTrash2 } from "react-icons/fi"

import { KnowledgeBasesService } from "@/client"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"

const DeleteKnowledgeBase = ({ id }: { id: string }) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useTranslation()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteKnowledgeBase = async (id: string) => {
    await KnowledgeBasesService.deleteKnowledgeBase({ id: id })
  }

  const mutation = useMutation({
    mutationFn: deleteKnowledgeBase,
    onSuccess: () => {
      showSuccessToast("The KnowledgeBase was deleted successfully")
      setIsOpen(false)
      // Force immediate cache invalidation and refetch
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
      queryClient.refetchQueries({ queryKey: ["knowledge-bases"] })
    },
    onError: () => {
      showErrorToast("An error occurred while deleting the KnowledgeBase")
    },
    onSettled: () => {
      // Additional invalidation on settlement
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
  })

  const onSubmit = async () => {
    mutation.mutate(id)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      role="alertdialog"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" colorPalette="red">
          <FiTrash2 fontSize="16px" />
          {t("knowledgeBases.deleteModal.buttonText")}
        </Button>
      </DialogTrigger>

      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogCloseTrigger />
          <DialogHeader>
            <DialogTitle>{t("knowledgeBases.deleteModal.title")}</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>{t("knowledgeBases.deleteModal.description")}</Text>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                {t("knowledgeBases.deleteModal.cancelButton")}
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              colorPalette="red"
              type="submit"
              loading={isSubmitting}
            >
              {t("knowledgeBases.deleteModal.confirmButton")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

export default DeleteKnowledgeBase
