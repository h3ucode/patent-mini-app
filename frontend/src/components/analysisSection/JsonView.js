import React from 'react';
import { Code } from '@chakra-ui/react';

export const JsonView = ({ analysisResult }) => (
  <Code 
    display="block" 
    whiteSpace="pre" 
    p={4}
    borderRadius="md"
    overflowX="auto"
  >
    {JSON.stringify(analysisResult, null, 2)}
  </Code>
); 