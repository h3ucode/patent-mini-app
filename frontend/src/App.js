import React from 'react';
import { 
  ChakraProvider, 
  Box, 
  VStack,
  Container,
  Heading,
  Tabs,
  TabList,
  TabPanels,
  TabPanel,
  Tab
} from '@chakra-ui/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { SelectionProvider } from './context/SelectionContext';
import { PatentDropdown } from './components/PatentDropdown';
import { CompanyDropdown } from './components/CompanyDropdown';
import { AnalysisSection } from './components/analysisSection/analysisSection';
import { SavedReports } from './components/SavedReports';
import { queryClient } from './config/graphqlClient';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SelectionProvider>
        <ChakraProvider>
          <Container maxW="container.md" py={8}>
            <VStack spacing={8} align="stretch">
              <Heading textAlign="center">Patent Infringement Checker</Heading>
              
              <Box 
                p={6} 
                borderWidth="1px" 
                borderRadius="lg" 
                boxShadow="sm"
              >
                <VStack spacing={6}>
                  <PatentDropdown />
                  <CompanyDropdown />
                  <Box width="100%">
                    <Tabs>
                      <TabList>
                      <Tab>Analysis</Tab>
                      <Tab>Saved Reports</Tab>
                    </TabList>
                    <TabPanels>
                      <TabPanel>
                        <AnalysisSection />
                      </TabPanel>
                      <TabPanel>
                        <SavedReports />
                      </TabPanel>
                    </TabPanels>
                    </Tabs>
                  </Box>
                </VStack>
              </Box>
            </VStack>
          </Container>
        </ChakraProvider>
      </SelectionProvider>
    </QueryClientProvider>
  );
}

export default App;
