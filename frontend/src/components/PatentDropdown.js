import React, { useState, useRef, useEffect } from 'react';
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
import { GET_PATENTS } from '../graphql/queries';
import { useSelection } from '../context/SelectionContext';

export const PatentDropdown = () => {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef();
  const { selectedPatent, setSelectedPatent } = useSelection();

  useOutsideClick({
    ref: dropdownRef,
    handler: () => setIsOpen(false),
  });

  const handleClear = () => {
    setSearch('');
    setSelectedPatent(null);
    setIsOpen(false);
  };

  const { data, isLoading } = useQuery({
    queryKey: ['patents', search],
    queryFn: async () => {
      const response = await graphqlClient.request(GET_PATENTS, {
        query: search,
        limit: 100
      });
    //   console.log('Fetched patents:', response.searchPatents);
      return response.searchPatents;
    }
  });

  const filteredPatents = data?.filter(patent => {
    if (!search) return true;
    
    const searchInput = search.toLowerCase().trim();
    const patentNumber = (patent.publicationNumber || '').toLowerCase();
    const patentTitle = (patent.title || '').toLowerCase();
    
    const searchableText = `${patentNumber} ${patentTitle}`;
    
    // console.log('Searching:', {
    //   searchInput,
    //   searchableText,
    //   patentNumber,
    //   patentTitle,
    // });

    if (patentNumber === searchInput) {
      return true;
    }

    if (searchableText.includes(searchInput)) {
      return true;
    }

    const searchTerms = searchInput.split(/[\s-]+/).filter(term => term.length > 0);
    return searchTerms.every(term => {
      return searchableText.includes(term.toLowerCase());
    });
  });

  const handleSelect = (patent) => {
    setSelectedPatent(patent);
    setSearch(patent.publicationNumber + ' - ' + patent.title);
    setIsOpen(false);
    // console.log('Selected patent:', patent);
  };


  return (
    <VStack width="100%" spacing={2} align="stretch" position="relative" ref={dropdownRef}>
      <Text fontWeight="bold">Select Patent</Text>
      <InputGroup>
        <Input
          placeholder="Search patents title..."
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
          ) : filteredPatents?.length ? (
            <List spacing={0}>
              {filteredPatents.map((patent) => (
                <ListItem
                  key={patent.patentId}
                  p={2}
                  cursor="pointer"
                  _hover={{ bg: 'gray.100' }}
                  onClick={() => handleSelect(patent)}
                >
                  <Text fontWeight="medium">{patent.publicationNumber}</Text>
                  <Text fontSize="sm" color="gray.600">{patent.title}</Text>
                </ListItem>
              ))}
            </List>
          ) : (
            <Box p={4} textAlign="center">
              <Text color="gray.500">No patents found</Text>
            </Box>
          )}
        </Box>
      )}
    </VStack>
  );
}; 