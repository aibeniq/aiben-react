import { Heading, Stack, VStack } from "@chakra-ui/react"
import { useTheme } from "next-themes"

import { Radio, RadioGroup } from "@/components/ui/radio"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm">Appearance</Heading>

      <RadioGroup
        onValueChange={(e) => setTheme(e.value || "system")}
        value={theme || "system"}
        colorPalette="teal"
      >
        <Stack>
          <Radio value="system">System</Radio>
          <Radio value="light">Light Mode</Radio>
          <Radio value="dark">Dark Mode</Radio>
        </Stack>
      </RadioGroup>
    </VStack>
  )
}

export default Appearance
