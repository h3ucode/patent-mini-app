import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  HStack,
} from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { graphqlClient } from '../config/graphqlClient';
import { GET_SAVED_ANALYSES, TOGGLE_SAVE_ANALYSIS } from '../graphql/queries';
import { PrettyView } from './analysisSection/PrettyView';

export const AnalysisSection = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedAnalysis, setSelectedAnalysis] = React.useState(null);
  const queryClient = useQueryClient();

  const { data: savedAnalyses, isLoading } = useQuery({
    queryKey: ['savedAnalyses'],
    queryFn: async () => {
      const response = await graphqlClient.request(GET_SAVED_ANALYSES);
      return response.savedAnalyses;
    }
  });

  const { mutate: toggleSave } = useMutation({
    mutationFn: async (isSaved) => {
      const response = await graphqlClient.request(TOGGLE_SAVE_ANALYSIS, {
        companyAnalysisId: analysisResult.companyAnalysisId,
        isSaved
      });
      return response.toggleSaveAnalysis;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['savedAnalyses']);
    }
  });

  const handleViewReport = (analysis) => {
    setSelectedAnalysis(analysis);
    onOpen();
  };

  return (
    <VStack spacing={4} align="stretch">
      <Heading size="md">Analysis Results</Heading>

      {savedAnalyses?.map((analysis) => (
        <Box
          key={analysis.companyAnalysisId}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          boxShadow="sm"
        >
          <VStack align="stretch" spacing={2}>
            <Text fontWeight="bold">
              {analysis.company.name} - {analysis.patent.publicationNumber}
            </Text>
            <Text fontSize="sm">{analysis.patent.title}</Text>
            <Text 
              color={
                analysis.overallRisk === 'High' ? 'red.500' :
                analysis.overallRisk === 'Medium' ? 'orange.500' : 'green.500'
              }
            >
              Risk Level: {analysis.overallRisk}
            </Text>
            <HStack justify="space-between" mb={4}>
              <Button size="sm" onClick={() => handleViewReport(analysis)}>
                View Full Report
              </Button>
              <Button
                size="sm"
                colorScheme={analysis.isSaved ? "green" : "gray"}
                onClick={() => toggleSave(!analysis.isSaved)}
              >
                {analysis.isSaved ? "Saved" : "Save Report"}
              </Button>
            </HStack>
          </VStack>
        </Box>
      ))}

      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Full Report</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {selectedAnalysis && <PrettyView analysisResult={selectedAnalysis} />}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
}; 