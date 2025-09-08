import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { KnowledgeBasePublic } from "@/client"
import EditKnowledgeBase from "@/components/KnowledgeBases/EditKnowledgeBase"
import DeleteKnowledgeBase from "../KnowledgeBases/DeleteKnowledgeBase"

interface KnowledgeBaseActionsMenuProps {
  item: KnowledgeBasePublic
}

export const KnowledgeBaseActionsMenu = ({
  item,
}: KnowledgeBaseActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditKnowledgeBase item={item} />
        <DeleteKnowledgeBase id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}
