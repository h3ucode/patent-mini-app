import React, { useState } from 'react';
import { 
  VStack,
  Button,
  Box,
  Text,
  Spinner,
  HStack,
  Heading,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { useSelection } from '../../context/SelectionContext';
import { PrettyView } from './PrettyView';
import { JsonView } from './JsonView';
import { useAnalysis } from './useAnalysis';
import { useIsMobile } from '../../hooks/useIsMobile';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { graphqlClient } from '../../config/graphqlClient';
import { TOGGLE_SAVE_ANALYSIS } from '../../graphql/queries';

export const AnalysisSection = () => {
  const isMobile = useIsMobile();
  const { selectedPatent, selectedCompany } = useSelection();
  const queryClient = useQueryClient();
  const [hasSaved, setHasSaved] = useState(false);
  // console.log('hasSaved', hasSaved);
  const {
    analysisResult,
    isAnalyzing,
    isLoadingAnalysis,
    isLoading,
    runAnalysis
  } = useAnalysis(selectedPatent, selectedCompany);

  // Reset hasSaved when new analysis is run
  const handleAnalyze = () => {
    setHasSaved(false);
    runAnalysis();
  };

  const { mutate: saveAnalysis, isLoading: isSaving } = useMutation({
    mutationFn: async () => {
      const response = await graphqlClient.request(TOGGLE_SAVE_ANALYSIS, {
        companyAnalysisId: analysisResult.companyAnalysisId,
        isSaved: true
      });
      return response.toggleSaveAnalysis;
    },
    onSuccess: () => {
      setHasSaved(true);
      queryClient.invalidateQueries(['savedAnalyses']);
    }
  });

  const canAnalyze = selectedPatent && selectedCompany;

  return (
    <VStack width="100%" spacing={4} align="stretch">
      <Box align="center">
        <Button
          colorScheme="blue"
          isDisabled={!canAnalyze || isLoading}
          isLoading={isLoading}
          loadingText="Analyzing... (This may take up to 10 seconds)"
          spinnerPlacement="end"
          width={isMobile ? "100%" : "60%"}
          onClick={handleAnalyze}
        >
          Analyze Patent Infringement
        </Button>
        {isLoading && (
          <Box mt={2} textAlign="center">
            <HStack spacing={2} justify="center">
              <Spinner size="sm" />
              <Text fontSize="sm" color="gray.600">
                {isAnalyzing 
                  ? "Running initial analysis..."
                  : "Fetching detailed results..."}
              </Text>
            </HStack>
          </Box>
        )}
      </Box>

      {analysisResult && (
        <Box
          mt={4}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg="white"
          boxShadow="sm"
        >
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between" align="center">
              <Heading size="md">Analysis Results</Heading>
              <Button
                size="sm"
                colorScheme={hasSaved ? "gray" : "green"}
                isDisabled={hasSaved}
                isLoading={isSaving}
                onClick={() => saveAnalysis()}
                
              >
                {hasSaved ? "Saved" : "Save Report"}
              </Button>
            </HStack>
            
            <Tabs>
              <TabList>
                <Tab>Pretty View</Tab>
                <Tab>JSON View</Tab>
              </TabList>

              <TabPanels>
                <TabPanel>
                  <PrettyView analysisResult={analysisResult} />
                </TabPanel>
                <TabPanel>
                  <JsonView analysisResult={analysisResult} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </VStack>
        </Box>
      )}
    </VStack>
  );
}; 