import { Box, Button, HStack, Text, VStack, Code } from "@chakra-ui/react"
import { useState, useEffect } from "react"
import {
  getProblematicOverlays,
  hasBlockingOverlays,
  cleanupOverlays,
  debugOverlays,
  OverlayInfo,
} from "../../utils/overlay-debugger"

interface OverlayDebuggerProps {
  isVisible?: boolean
}

const OverlayDebugger = ({ isVisible = false }: OverlayDebuggerProps) => {
  const [overlays, setOverlays] = useState<OverlayInfo[]>([])
  const [hasBlocking, setHasBlocking] = useState(false)
  const [lastCleanupCount, setLastCleanupCount] = useState(0)

  const refreshOverlayInfo = () => {
    const currentOverlays = getProblematicOverlays()
    const blocking = hasBlockingOverlays()

    setOverlays(currentOverlays)
    setHasBlocking(blocking)

    console.log("🔍 Overlay refresh:", {
      total: currentOverlays.length,
      blocking: blocking,
      overlays: currentOverlays,
    })
  }

  const handleCleanup = () => {
    const cleaned = cleanupOverlays()
    setLastCleanupCount(cleaned)
    refreshOverlayInfo()
    console.log(`🔧 Cleaned up ${cleaned} overlays`)
  }

  const handleDebug = () => {
    debugOverlays()
  }

  useEffect(() => {
    if (isVisible) {
      refreshOverlayInfo()

      // Set up periodic refresh
      const interval = setInterval(refreshOverlayInfo, 2000)
      return () => clearInterval(interval)
    }
  }, [isVisible])

  if (!isVisible) {
    return null
  }

  return (
    <Box
      position="fixed"
      top="4"
      left="4"
      bg="white"
      border="2px solid"
      borderColor="red.500"
      borderRadius="md"
      p={4}
      zIndex={10000}
      boxShadow="lg"
      maxW="400px"
      maxH="80vh"
      overflowY="auto"
    >
      <VStack align="stretch" gap={3}>
        <Text fontWeight="bold" color="red.600">
          🔍 Overlay Debugger
        </Text>

        <HStack gap={2}>
          <Button size="sm" onClick={refreshOverlayInfo}>
            Refresh
          </Button>
          <Button size="sm" colorScheme="orange" onClick={handleCleanup}>
            Clean Up
          </Button>
          <Button size="sm" colorScheme="blue" onClick={handleDebug}>
            Console Debug
          </Button>
        </HStack>

        <Box>
          <Text fontSize="sm" fontWeight="medium">
            Status:
          </Text>
          <HStack gap={2}>
            <Text fontSize="sm" color={hasBlocking ? "red.600" : "green.600"}>
              {hasBlocking ? "⚠️ Blocking overlays detected" : "✅ No blocking overlays"}
            </Text>
          </HStack>

          {lastCleanupCount > 0 && (
            <Text fontSize="sm" color="blue.600">
              Last cleanup: {lastCleanupCount} overlays removed
            </Text>
          )}
        </Box>

        <Box>
          <Text fontSize="sm" fontWeight="medium" mb={2}>
            Found Overlays ({overlays.length}):
          </Text>
          <VStack align="stretch" gap={1} maxH="200px" overflowY="auto">
            {overlays.length === 0 ? (
              <Text fontSize="xs" color="gray.500">
                No overlays found
              </Text>
            ) : (
              overlays.map((overlay, index) => (
                <Box key={index} p={2} bg="gray.50" borderRadius="sm">
                  <Code fontSize="xs" mb={1}>
                    {overlay.selector}
                  </Code>
                  <HStack gap={2} fontSize="xs">
                    <Text>z-index: {overlay.zIndex}</Text>
                    <Text>opacity: {overlay.opacity}</Text>
                    <Text>display: {overlay.display}</Text>
                  </HStack>
                  <Text fontSize="xs" color="gray.600">
                    pointer-events: {overlay.pointerEvents}
                  </Text>
                </Box>
              ))
            )}
          </VStack>
        </Box>

        <Box fontSize="xs" color="gray.600">
          <Text fontWeight="medium">Emergency shortcuts:</Text>
          <Text>Ctrl+Shift+F12: Clean up overlays</Text>
          <Text>Ctrl+Shift+F11: Console debug info</Text>
        </Box>
      </VStack>
    </Box>
  )
}

export default OverlayDebugger
