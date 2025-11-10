import { CloseButton, Dialog, HStack, Heading, Portal, Switch, Text } from "@chakra-ui/react"
import type React from "react"
import { useTranslation } from "react-i18next"
import { DialogBody, DialogFooter, DialogHeader } from "../ui/dialog"
import ConfirmButton from "../ui/confirm-button"
import HelpTooltip from "../ui/help-tooltip"
import { Tooltip } from "../ui/tooltip"

interface SelectionModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  // Optional toggle props
  showToggle?: boolean
  toggleLabel?: string
  toggleValue?: boolean
  onToggleChange?: () => void
  toggleTooltipContent?: string
}

const SelectionModal = ({
  isOpen,
  onClose,
  title,
  children,
  showToggle = false,
  toggleLabel = "",
  toggleValue = false,
  onToggleChange,
  toggleTooltipContent = "",
}: SelectionModalProps) => {
  const { t } = useTranslation()

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={({ open }) => !open && onClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner style={{ zIndex: 2000 }}>
          <Dialog.Content maxW="4xl" maxH="80vh">
            <DialogHeader>
              <HStack justify="space-between" align="center" w="full">
                <Heading size="lg">{title}</Heading>
                <CloseButton size="xl" onClick={onClose} variant="ghost" />
              </HStack>
              {/* Toggle section */}
              {showToggle && (
                <HStack justifyContent="flex-end" mt={2}>
                  <Tooltip content={toggleTooltipContent}>
                    <HStack gap={2}>
                      <HStack gap={1} align="center">
                        <Text fontSize="xs" color="gray.500">
                          {toggleLabel}
                        </Text>
                        <HelpTooltip helpKey="allUsersToggle" />
                      </HStack>
                      <Switch.Root
                        key={`switch-${toggleValue}`}
                        size="sm"
                        colorPalette="blue"
                        checked={toggleValue}
                      >
                        <Switch.HiddenInput checked={toggleValue} onChange={onToggleChange} />
                        <Switch.Control data-state={toggleValue ? "checked" : "unchecked"}>
                          <Switch.Thumb />
                        </Switch.Control>
                      </Switch.Root>
                    </HStack>
                  </Tooltip>
                </HStack>
              )}
            </DialogHeader>
            <DialogBody>{children}</DialogBody>
            <DialogFooter justifyContent="flex-end">
              <ConfirmButton onClick={onClose} size="md">
                {t("buttons.done")}
              </ConfirmButton>
            </DialogFooter>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </Portal>
  )
}

export default SelectionModal
