import { Heading, Stack, VStack } from "@chakra-ui/react"
import { useTheme } from "next-themes"
import { Radio, RadioGroup } from "../ui/radio"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm" color="fg">
        Appearance
      </Heading>

      <RadioGroup
        onValueChange={(details) => setTheme(details.value || "system")}
        value={theme || "system"}
        colorPalette="teal"
      >
        <Stack>
          <Radio value="system" color="fg">
            System
          </Radio>
          <Radio value="light" color="fg">
            Light Mode
          </Radio>
          <Radio value="dark" color="fg">
            Dark Mode
          </Radio>
        </Stack>
      </RadioGroup>
    </VStack>
  )
}

export default Appearance
