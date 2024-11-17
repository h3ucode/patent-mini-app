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
  Tabs,
  TabList,
  TabPanels,
  TabPanel,
  Tab,
  HStack,
  Badge,
  Stack
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { graphqlClient } from '../config/graphqlClient';
import { GET_SAVED_ANALYSES } from '../graphql/queries';
import { PrettyView } from './analysisSection/PrettyView';
import { JsonView } from './analysisSection/JsonView';
import { useSelection } from '../context/SelectionContext';
import { useIsMobile } from '../hooks/useIsMobile';
export const SavedReports = () => {
  const isMobile = useIsMobile();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedAnalysis, setSelectedAnalysis] = React.useState(null);
  const { selectedCompany } = useSelection();
  const { data: savedAnalyses, isLoading } = useQuery({
    queryKey: ['savedAnalyses'],
    queryFn: async () => {
      const response = await graphqlClient.request(GET_SAVED_ANALYSES);
      return response.savedAnalyses;
    }
  });

  // Filter analyses based on selected company
  const filteredAnalyses = React.useMemo(() => {
    if (!savedAnalyses) return [];
    if (!selectedCompany || !selectedCompany.name) return savedAnalyses;
    
    
    return savedAnalyses.filter(analysis => 
      analysis.company.name === selectedCompany.name
    );
  }, [savedAnalyses, selectedCompany]);

  const handleViewReport = (analysis) => {
    setSelectedAnalysis(analysis);
    onOpen();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (isLoading) return <Text>Loading saved reports...</Text>;

  return (
    <VStack spacing={4} align="stretch">
      <Heading size="md">
        {selectedCompany?.name 
          ? `Saved Reports for ${selectedCompany.name}`
          : 'All Saved Reports'}
      </Heading>

      {filteredAnalyses.length === 0 && (
        <Text color="gray.500">
          {selectedCompany?.name 
            ? `No saved reports found for ${selectedCompany.name}`
            : 'No saved reports found'}
        </Text>
      )}

      {filteredAnalyses.map((analysis) => (
        <Box
          key={analysis.companyAnalysisId}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          boxShadow="sm"
        >
          <VStack align="stretch" spacing={2}>
            <HStack justify="space-between">
              <Text fontWeight="bold">
                {analysis.company.name} - {analysis.patent.publicationNumber}
              </Text>
              <Badge colorScheme="green">
                Saved: {formatDate(analysis.isSavedAt)}
              </Badge>
            </HStack>
            <Text fontSize="sm">{analysis.patent.title}</Text>
            <Text 
              color={
                analysis.overallRisk === 'High' ? 'red.500' :
                analysis.overallRisk === 'Medium' ? 'orange.500' : 'green.500'
              }
            >
              Risk Level: {analysis.overallRisk}
            </Text>
            <Button size="sm" onClick={() => handleViewReport(analysis)}>
              View Full Report
            </Button>
          </VStack>
        </Box>
      ))}

      <Modal isOpen={isOpen} onClose={onClose} size="4xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <Stack direction={isMobile ? "column" : "row"} justify="space-between" py={4}>
              <Text>Full Report</Text>
              {selectedAnalysis && 
              <Badge colorScheme="green" px={2}>
                Saved: {formatDate(selectedAnalysis.isSavedAt)}
              </Badge>
              }
            </Stack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {selectedAnalysis && 
            <Tabs>
              <TabList>
                <Tab>Pretty View</Tab>
                <Tab>JSON View</Tab>
              </TabList>

              <TabPanels>
                <TabPanel>
                <PrettyView analysisResult={selectedAnalysis} />
                </TabPanel>
                <TabPanel>
                  <JsonView analysisResult={selectedAnalysis} />
                </TabPanel>
              </TabPanels>
            </Tabs>
            }
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
}; 


