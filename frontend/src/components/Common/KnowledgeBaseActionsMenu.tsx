import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { KnowledgeBasePublic } from "@/client"
import DeleteItem from "../Items/DeleteItem"
import EditItem from "../Items/EditItem"

interface KnowledgeBaseActionsMenuProps {
  item: KnowledgeBasePublic
}

export const KnowledgeBaseActionsMenu = ({ item }: KnowledgeBaseActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditItem item={item} />
        <DeleteItem id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}
