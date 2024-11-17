import React, { useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Input,
  VStack,
  Text,
  Spinner,
  List,
  ListItem,
  useOutsideClick,
  InputGroup,
  InputRightElement,
  IconButton,
} from '@chakra-ui/react';
import { CloseIcon } from '@chakra-ui/icons';
import { graphqlClient } from '../config/graphqlClient';
import { GET_COMPANIES } from '../graphql/queries';
import { useSelection } from '../context/SelectionContext';

export const CompanyDropdown = () => {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef();
  const { selectedCompany, setSelectedCompany } = useSelection();

  useOutsideClick({
    ref: dropdownRef,
    handler: () => setIsOpen(false),
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const response = await graphqlClient.request(GET_COMPANIES);
      return response.companies;
    }
  });

  const handleClear = () => {
    setSearch('');
    setSelectedCompany(null);
    setIsOpen(false);
  };

  const filteredCompanies = data?.filter(company => {
    if (!search) return true;
    const searchInput = search.toLowerCase().trim();
    const companyName = (company.name || '').toLowerCase();
    // Direct match
    if (companyName === searchInput) {
      return true;
    }
    // Partial match
    if (companyName.includes(searchInput)) {
      return true;
    }
    // Word by word match
    const searchWords = searchInput.split(/\s+/);
    const matchesWords = searchWords.every(word => 
      companyName.includes(word)
    );
    return matchesWords;
  });

  const handleSelect = (company) => {
    setSelectedCompany(company);
    setSearch(company.name);
    setIsOpen(false);
  };

  if (error) return <Text color="red.500">Error loading companies</Text>;

  return (
    <VStack width="100%" spacing={2} align="stretch" position="relative" ref={dropdownRef}>
      <Text fontWeight="bold">Select Company</Text>
      <InputGroup>
        <Input
          placeholder="Search companies..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
        />
        {search && (
          <InputRightElement>
            <IconButton
              icon={<CloseIcon />}
              size="sm"
              variant="ghost"
              onClick={handleClear}
              aria-label="Clear selection"
            />
          </InputRightElement>
        )}
      </InputGroup>
      
      {isOpen && (
        <Box
          position="absolute"
          top="100%"
          left={0}
          right={0}
          zIndex={1}
          bg="white"
          borderWidth="1px"
          borderRadius="md"
          boxShadow="lg"
          maxH="300px"
          overflowY="auto"
          mt={1}
        >
          {isLoading ? (
            <Box p={4} textAlign="center">
              <Spinner />
            </Box>
          ) : filteredCompanies?.length ? (
            <List spacing={0}>
              {filteredCompanies.map((company) => (
                <ListItem
                  key={company.companyId}
                  p={2}
                  cursor="pointer"
                  _hover={{ bg: 'gray.100' }}
                  onClick={() => handleSelect(company)}
                >
                  <Text fontWeight="medium">{company.name}</Text>
                </ListItem>
              ))}
            </List>
          ) : (
            <Box p={4} textAlign="center">
              <Text color="gray.500">No companies found</Text>
            </Box>
          )}
        </Box>
      )}
    </VStack>
  );
}; 