import React from "react"
import { Box, Text, Heading } from "@chakra-ui/react"

interface TopicAnalysisDisplayProps {
  topicAnalysis: any[]
}

const TopicAnalysisDisplay: React.FC<TopicAnalysisDisplayProps> = ({ topicAnalysis }) => {
  if (topicAnalysis.length === 0) return null

  return (
    <Box mt={4}>
      {topicAnalysis.map((topic: any, index: number) => (
        <Box key={index} mb={4} p={4} borderWidth="1px" borderRadius="md" bg="white">
          <Heading as="h3" size="md" mb={2}>
            Topic: {topic.topic}
          </Heading>
          <Text>{topic.analysis}</Text>
        </Box>
      ))}
    </Box>
  )
}

export default TopicAnalysisDisplay
