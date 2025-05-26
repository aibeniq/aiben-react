import { Box, Flex, Icon, Text, Accordion } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink } from "@tanstack/react-router"
import { FiBriefcase, FiHome, FiSettings, FiUsers, FiBookOpen, FiClipboard, FiTool, FiPackage, FiFileText } from "react-icons/fi"
import { TbPlugConnected } from "react-icons/tb";
import type { IconType } from "react-icons/lib"

import type { UserPublic } from "@/client"

// Define categories with their items
const categories = [
  {
    name: null, // No category header for these items
    items: [
      { icon: FiHome, title: "Dashboard", path: "/" },
    ]
  },
  {
    name: "Tools",
    icon: FiTool,
    items: [
      { icon: FiClipboard, title: "VeraDoc", path: "/veradoc" },
      { icon: FiFileText, title: "ReportGenie", path: "/reportgenie" },
      { icon: TbPlugConnected, title: "FormConnect", path: "/formconnect" },
    ]
  },
  {
    name: "Configurations",
    icon: FiPackage,
    items: [
      { icon: FiTool, title: "Model Selection", path: "/model-selection" },
      { icon: FiBookOpen, title: "Knowledge Bases", path: "/knowledge-bases" },
      { icon: FiSettings, title: "User Settings", path: "/settings" },
    ]
  }
];

// Admin item for superusers
const adminItem = { icon: FiUsers, title: "Admin", path: "/admin" };

interface SidebarItemsProps {
  onClose?: () => void
}

interface Item {
  icon: IconType
  title: string
  path: string
}

interface Category {
  name: string | null
  icon?: IconType
  items: Item[]
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  // Add admin item for superusers
  const finalCategories = [...categories];
  if (currentUser?.is_superuser) {
    finalCategories.push({
      name: null,
      items: [adminItem]
    });
  }
  
  return (
    <Box>
      {finalCategories.map((category, index) => (
        <Box key={index} mb={4}>
          {category.name ? (
            // Render category with expandable items
            <Accordion.Root multiple defaultValue={["tools", "configurations"]}>
              <Accordion.Item border="none" value={category.name.toLowerCase()}>
                <Accordion.ItemTrigger px={4} py={2} _hover={{ bg: "gray.subtle" }}>
                  <Box as="span" flex='1' textAlign='left'>
                    <Flex alignItems="center">
                      {category.icon && <Icon as={category.icon} mr={2} />}
                      <Text fontSize="xs" fontWeight="bold">{category.name}</Text>
                    </Flex>
                  </Box>
                </Accordion.ItemTrigger>
                <Accordion.ItemContent p={0}>
                  {category.items.map((item) => (
                    <RouterLink key={item.title} to={item.path} onClick={onClose}>
                      <Flex
                        gap={4}
                        pl={8} // Extra padding to indicate nesting
                        pr={4}
                        py={2}
                        _hover={{
                          background: "gray.subtle",
                        }}
                        alignItems="center"
                        fontSize="sm"
                      >
                        <Icon as={item.icon} alignSelf="center" />
                        <Text ml={2}>{item.title}</Text>
                      </Flex>
                    </RouterLink>
                  ))}
                </Accordion.ItemContent>
              </Accordion.Item>
            </Accordion.Root>
          ) : (
            // Render items without category
            <>
              {index === 0 && (
                <Text fontSize="xs" px={4} py={2} fontWeight="bold">
                  Menu
                </Text>
              )}
              {category.items.map((item) => (
                <RouterLink key={item.title} to={item.path} onClick={onClose}>
                  <Flex
                    gap={4}
                    px={4}
                    py={2}
                    _hover={{
                      background: "gray.subtle",
                    }}
                    alignItems="center"
                    fontSize="sm"
                  >
                    <Icon as={item.icon} alignSelf="center" />
                    <Text ml={2}>{item.title}</Text>
                  </Flex>
                </RouterLink>
              ))}
            </>
          )}
        </Box>
      ))}
    </Box>
  )
}

export default SidebarItems