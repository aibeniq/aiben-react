import { HStack, VStack, Input, Textarea, Dialog, Portal, CloseButton } from "@chakra-ui/react"
import { Field } from "../ui/field"
import { TwinCheckTopicList } from "../../client"
import TopicItem from "./TopicItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"

interface TopicListModalProps {
  isOpen: boolean
  onClose: () => void
  editingTopicList: TwinCheckTopicList | null
  onSave: () => void
  topicListName: string
  setTopicListName: (name: string) => void
  topicListDescription: string
  setTopicListDescription: (description: string) => void
  topicsList: string[]
  updateTopic: (index: number, value: string) => void
  handleTopicBlur: (index: number, value: string) => void
  removeTopic: (index: number) => void
  moveTopicUp: (index: number) => void
  moveTopicDown: (index: number) => void
}

const TopicListModal = ({
  isOpen,
  onClose,
  editingTopicList,
  onSave,
  topicListName,
  setTopicListName,
  topicListDescription,
  setTopicListDescription,
  topicsList,
  updateTopic,
  handleTopicBlur,
  removeTopic,
  moveTopicUp,
  moveTopicDown,
}: TopicListModalProps) => {
  return (
    <Dialog.Root open={isOpen} onOpenChange={(e) => (e.open ? null : onClose())}>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="4xl" maxH="90vh">
            <Dialog.Header>
              <Dialog.Title>
                {editingTopicList ? "Edit Topic List" : "Create New Topic List"}
              </Dialog.Title>
            </Dialog.Header>

            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                <HStack align="stretch" gap={4}>
                  <VStack align="stretch" gap={4} flex="1">
                    <Field label="Topic List Name" required>
                      <Input
                        value={topicListName}
                        onChange={(e) => setTopicListName(e.target.value)}
                        placeholder="Enter topic list name"
                      />
                    </Field>

                    <Field label="Topic List Description">
                      <Textarea
                        value={topicListDescription}
                        onChange={(e) => setTopicListDescription(e.target.value)}
                        placeholder="Enter topic list description"
                        resize="vertical"
                      />
                    </Field>
                  </VStack>

                  <Field label="Comparison Topics" required py={0} flex="1">
                    <VStack
                      align="stretch"
                      gap={0}
                      display="flex"
                      flexDirection="column"
                      width="100%"
                      maxH="300px"
                      overflowY="auto"
                    >
                      {topicsList.map((topic, index) => (
                        <TopicItem
                          key={index}
                          index={index}
                          topic={topic}
                          onUpdate={updateTopic}
                          onBlur={handleTopicBlur}
                          onRemove={removeTopic}
                          onMoveUp={moveTopicUp}
                          onMoveDown={moveTopicDown}
                          canRemove={topicsList.length > 1 && topic.trim() !== ""}
                          totalTopics={topicsList.length}
                        />
                      ))}
                    </VStack>
                  </Field>
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <CancelButton onClick={onClose} size="md">
                  Cancel
                </CancelButton>
              </Dialog.ActionTrigger>
              <ConfirmButton onClick={onSave} size="md">
                {editingTopicList ? "Update Topic List" : "Create Topic List"}
              </ConfirmButton>
            </Dialog.Footer>

            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  )
}

export default TopicListModal
