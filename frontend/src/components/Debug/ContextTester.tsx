import React from 'react'
import { Button, VStack, Text, Box } from '@chakra-ui/react'
import { useResults } from '../../contexts/ResultsContext'

export const ContextTester: React.FC = () => {
  const {
    reviewResults,
    setReviewResults,
    generateResult,
    setGenerateResult,
    compareResult,
    setCompareResult,
    matchResult,
    setMatchResult,
    clearReviewResults,
    clearGenerateResult,
    clearCompareResult,
    clearMatchResult
  } = useResults()

  const testReview = () => {
    setReviewResults([
      {
        filename: 'test-file.pdf',
        displayResults: 'Test review results',
        qaPairs: [
          {
            question: 'Test question?',
            answer: 'Test answer',
            context: 'Test context'
          }
        ],
        interactionId: 'test-review-123'
      }
    ])
  }

  const testGenerate = () => {
    setGenerateResult({
      full_report: '# Test Report\n\nThis is a test generated report.',
      sections: [
        {
          title: 'Test Section',
          content: 'Test section content'
        }
      ],
      interactionId: 'test-generate-123'
    })
  }

  const testCompare = () => {
    setCompareResult({
      summary: 'Test comparison summary',
      topicResults: [
        {
          topic: 'Test Topic',
          analysis: 'Test analysis'
        }
      ],
      interactionId: 'test-compare-123'
    })
  }

  const testMatch = () => {
    setMatchResult({
      results: 'Test match results\n\nThis is a test match output.',
      interactionId: 'test-match-123'
    })
  }

  return (
    <Box 
      position="fixed" 
      bottom={4} 
      left={4} 
      bg="blue.500" 
      color="white" 
      p={4} 
      borderRadius="md" 
      zIndex={9999}
      maxWidth="300px"
    >
      <VStack gap={2}>
        <Text fontWeight="bold" fontSize="sm">Context Tester</Text>
        
        <VStack gap={1} fontSize="xs">
          <Text>Review: {reviewResults.length} results</Text>
          <Text>Generate: {generateResult ? 'Yes' : 'No'}</Text>
          <Text>Compare: {compareResult ? 'Yes' : 'No'}</Text>
          <Text>Match: {matchResult ? 'Yes' : 'No'}</Text>
        </VStack>

        <VStack gap={1}>
          <Button size="xs" onClick={testReview}>Test Review</Button>
          <Button size="xs" onClick={testGenerate}>Test Generate</Button>
          <Button size="xs" onClick={testCompare}>Test Compare</Button>
          <Button size="xs" onClick={testMatch}>Test Match</Button>
        </VStack>

        <VStack gap={1}>
          <Button size="xs" colorScheme="red" onClick={clearReviewResults}>Clear Review</Button>
          <Button size="xs" colorScheme="red" onClick={clearGenerateResult}>Clear Generate</Button>
          <Button size="xs" colorScheme="red" onClick={clearCompareResult}>Clear Compare</Button>
          <Button size="xs" colorScheme="red" onClick={clearMatchResult}>Clear Match</Button>
        </VStack>
      </VStack>
    </Box>
  )
}
