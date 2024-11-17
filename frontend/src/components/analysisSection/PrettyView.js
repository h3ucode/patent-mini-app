import React from 'react';
import { 
  VStack,
  Box,
  Text,
  Code,
  Heading,
  Divider,
  UnorderedList,
  ListItem,
} from '@chakra-ui/react';

export const PrettyView = ({ analysisResult }) => {
  // Sort product analyses by number of relevant claims
  const sortedProductAnalyses = [...analysisResult.productAnalyses.edges].sort((a, b) => {
    const aClaimsLength = a.node.relevantClaimsList?.length || 0;
    const bClaimsLength = b.node.relevantClaimsList?.length || 0;
    return bClaimsLength - aClaimsLength; // Sort in descending order
  });

  return (
    <VStack spacing={4} align="stretch">
      <Box>
        <Text fontWeight="bold">Company: {analysisResult.company.name}</Text>
        <Text fontWeight="bold" color={
          analysisResult.overallRisk === 'High' ? 'red.500' :
          analysisResult.overallRisk === 'Medium' ? 'orange.500' : 'green.500'
        }>
          Overall Risk: {analysisResult.overallRisk}
        </Text>
        <Text>{analysisResult.overallRiskAssessment}</Text>
      </Box>

      <Divider />

      <Box>
        <Heading size="sm" mb={2}>Top 2 Potentially Infringement Products Analysis</Heading>
        <VStack spacing={4} align="stretch">
          {sortedProductAnalyses.map(({ node }, index) => (
            <Box 
              key={index}
              p={4}
              borderWidth="1px"
              borderRadius="md"
              bg="gray.50"
            >
              <Text fontWeight="bold">{node.product.name}</Text>
              <Text fontSize="sm" color="gray.600" mb={2}>
                {node.product.description}
              </Text>
              <Text 
                fontWeight="bold"
                color={
                  node.infringementLikelihood === 'High' ? 'red.500' :
                  node.infringementLikelihood === 'Medium' ? 'orange.500' : 'green.500'
                }
              >
                Infringement Likelihood: {node.infringementLikelihood}
              </Text>
              <Text mt={2}>Explanation: {node.explanation}</Text>
              
              {node.relevantClaimsList?.length > 0 && (
                <Box mt={2}>
                  <Text fontWeight="bold">Relevant Claims:</Text>
                  <Code p={2} borderRadius="md" display="block">
                    {node.relevantClaimsList.join(', ')}
                  </Code>
                </Box>
              )}
              
              {node.specificFeaturesList?.length > 0 && (
                <Box mt={2}>
                  <Text fontWeight="bold">Specific Features:</Text>
                  <UnorderedList pl={4} spacing={1}>
                    {node.specificFeaturesList.map((feature, idx) => (
                      <ListItem key={idx}>{feature}</ListItem>
                    ))}
                  </UnorderedList>
                </Box>
              )}
            </Box>
          ))}
        </VStack>
      </Box>
    </VStack>
  );
}; 