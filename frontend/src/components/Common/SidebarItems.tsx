import { Accordion, Box, Flex, Icon, Text } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink, useRouterState } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { FaBalanceScale } from "react-icons/fa"
import {
  FiArchive,
  FiCheckCircle,
  FiCpu,
  FiDatabase,
  FiFilePlus,
  FiHome,
  FiPackage,
  FiSettings,
  FiTool,
  FiUsers,
} from "react-icons/fi"
import type { IconType } from "react-icons/lib"
import { TbPlugConnected } from "react-icons/tb"
import HelpTooltip from "../ui/help-tooltip"

import type { UserPublic } from "@/client"

interface SidebarItemsProps {
  onClose?: () => void
}

interface Item {
  icon: IconType
  title: string
  path: string
  helpKey?: string // Optional help key for tooltip
}

interface Category {
  name: string | null
  icon?: IconType
  items: Item[]
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const routerState = useRouterState()
  const { t } = useTranslation()

  // Define categories with their items
  const categories: Category[] = [
    {
      name: null, // No category header for these items
      items: [
        {
          icon: FiHome,
          title: t("navigation.dashboard"),
          path: "/",
          helpKey: "dashboard",
        },
      ],
    },
    {
      name: t("navigation.tools"),
      icon: FiTool,
      items: [
        {
          icon: FiCheckCircle,
          title: t("navigation.review"),
          path: "/review",
          helpKey: "review",
        },
        {
          icon: FiFilePlus,
          title: t("navigation.generate"),
          path: "/generate",
          helpKey: "generate",
        },
        {
          icon: FaBalanceScale,
          title: t("navigation.compare"),
          path: "/compare",
          helpKey: "compare",
        },
        {
          icon: TbPlugConnected,
          title: t("navigation.match"),
          path: "/match",
          helpKey: "match",
        },
      ],
    },
    {
      name: t("navigation.configurations"),
      icon: FiPackage,
      items: [
        {
          icon: FiCpu,
          title: t("navigation.modelSelection"),
          path: "/model-selection",
          helpKey: "modelSelection",
        },
        {
          icon: FiDatabase,
          title: t("navigation.knowledgeBases"),
          path: "/knowledge-bases",
          helpKey: "knowledgeBases",
        },
        {
          icon: FiArchive,
          title: t("navigation.archive"),
          path: "/archive",
          helpKey: "archive",
        },
        {
          icon: FiSettings,
          title: t("navigation.settings"),
          path: "/settings",
          helpKey: "settings",
        },
      ],
    },
  ]

  // Get all category names that have accordions (not null names)
  const getAllAccordionCategories = () => {
    return categories
      .filter((category) => category.name !== null)
      .map((category) => category.name!.toLowerCase())
  }

  // Accordion state persistence - all accordions open by default
  const [expandedItems, setExpandedItems] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem("sidebar-accordion-state")
      // Always ensure all accordions are included in default state
      const defaultExpanded = getAllAccordionCategories()
      return saved ? JSON.parse(saved) : defaultExpanded
    } catch {
      // Fallback to all accordions open
      return getAllAccordionCategories()
    }
  })

  // Save accordion state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(
      "sidebar-accordion-state",
      JSON.stringify(expandedItems),
    )
  }, [expandedItems])

  // Utility function to reset all accordions to open state (for debugging)
  // Uncomment the following lines if you need to force reset:
  // useEffect(() => {
  //   const defaultExpanded = getAllAccordionCategories()
  //   setExpandedItems(defaultExpanded)
  // }, []) // Run once on mount to force reset

  // Admin item for superusers
  const adminItem = {
    icon: FiUsers,
    title: t("navigation.admin"),
    path: "/admin",
    helpKey: "admin",
  }

  // Fetch system configuration to check if model selection is enabled
  const { data: systemConfig } = useQuery({
    queryKey: ["systemConfig"],
    queryFn: async () => {
      // Temporary implementation - this will be replaced when SDK is regenerated
      const response = await fetch("/api/v1/utils/system-config")
      if (!response.ok) {
        throw new Error("Failed to fetch system config")
      }
      return response.json()
    },
    // Default to enabling model selection if the query fails
    retry: 3,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Filter categories based on system configuration
  const getFilteredCategories = () => {
    const filtered = [...categories]

    // If model selection is disabled, remove it from configurations
    // Default to showing model selection if config is not available (fail-safe)
    if (systemConfig?.enable_model_selection === false) {
      const configIndex = filtered.findIndex(
        (category) => category.name === t("navigation.configurations"),
      )
      if (configIndex !== -1) {
        filtered[configIndex] = {
          ...filtered[configIndex],
          items: filtered[configIndex].items.filter(
            (item: Item) => item.path !== "/model-selection",
          ),
        }
      }
    }

    return filtered
  }

  // Add admin item for superusers
  const finalCategories = getFilteredCategories()
  if (currentUser?.is_superuser) {
    finalCategories.push({
      name: null,
      items: [adminItem],
    })
  }

  const isActiveItem = (itemPath: string) => {
    return routerState.location.pathname === itemPath
  }

  return (
    <Box>
      {finalCategories.map((category, index) => (
        <Box key={index} mb={4}>
          {category.name ? (
            // Render category with expandable items
            <Accordion.Root
              multiple
              value={expandedItems}
              onValueChange={(details) => setExpandedItems(details.value)}
            >
              <Accordion.Item border="none" value={category.name.toLowerCase()}>
                <Accordion.ItemTrigger
                  px={4}
                  py={2}
                  _hover={{ bg: "gray.subtle" }}
                >
                  <Box as="span" flex="1" textAlign="left">
                    <Flex alignItems="center">
                      {category.icon && <Icon as={category.icon} mr={2} />}
                      <Text fontSize="xs" fontWeight="bold">
                        {category.name}
                      </Text>
                    </Flex>
                  </Box>
                </Accordion.ItemTrigger>
                <Accordion.ItemContent p={0}>
                  {category.items.map((item: Item) => (
                    <RouterLink
                      key={item.title}
                      to={item.path}
                      onClick={onClose}
                    >
                      <Flex
                        gap={4}
                        pl={8} // Extra padding to indicate nesting
                        pr={4}
                        py={2}
                        bg={
                          isActiveItem(item.path) ? "gray.100" : "transparent"
                        }
                        color={
                          isActiveItem(item.path)
                            ? "rgba(0, 65, 72, 1.0)"
                            : "inherit"
                        }
                        _hover={{
                          background: isActiveItem(item.path)
                            ? "blue.subtle"
                            : "gray.subtle",
                        }}
                        alignItems="center"
                        fontSize="sm"
                        fontWeight={
                          isActiveItem(item.path) ? "semibold" : "normal"
                        }
                      >
                        <Icon as={item.icon} alignSelf="center" />
                        <Text ml={2}>{item.title}</Text>
                        {item.helpKey && <HelpTooltip helpKey={item.helpKey} />}
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
                  {t("navigation.menu")}
                </Text>
              )}
              {category.items.map((item: Item) => (
                <RouterLink key={item.title} to={item.path} onClick={onClose}>
                  <Flex
                    gap={4}
                    px={4}
                    py={2}
                    bg={isActiveItem(item.path) ? "blue.subtle" : "transparent"}
                    color={isActiveItem(item.path) ? "blue.fg" : "inherit"}
                    _hover={{
                      background: isActiveItem(item.path)
                        ? "blue.subtle"
                        : "gray.subtle",
                    }}
                    alignItems="center"
                    fontSize="sm"
                    fontWeight={isActiveItem(item.path) ? "semibold" : "normal"}
                  >
                    <Icon as={item.icon} alignSelf="center" />
                    <Text ml={2}>{item.title}</Text>
                    {item.helpKey && <HelpTooltip helpKey={item.helpKey} />}
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
