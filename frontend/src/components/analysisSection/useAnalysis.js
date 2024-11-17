import { useMutation, useQuery } from '@tanstack/react-query';
import { useToast } from '@chakra-ui/react';
import { graphqlClient } from '../../config/graphqlClient';
import { ANALYZE_COMPANY_AGAINST_PATENT, GET_COMPANY_ANALYSIS } from '../../graphql/queries';
import { useState } from 'react';
export const useAnalysis = (selectedPatent, selectedCompany) => {
  const toast = useToast();
  const [analysisId, setAnalysisId] = useState(null);

  const { data: analysisResult, isPending: isLoadingAnalysis, refetch: refetchAnalysis } = useQuery({
    queryKey: ['companyAnalysis', analysisId],
    queryFn: async () => {
      const response = await graphqlClient.request(GET_COMPANY_ANALYSIS, {
        companyAnalysisId: analysisId
      });
      return response.companyAnalysis;
    },
    enabled: !!analysisId
  });

  const isQueryLoading = !analysisId ? false: isLoadingAnalysis;

  const { mutate,  isPending: isAnalyzing } = useMutation({
    mutationKey: ['analyzeCompanyAgainstPatent'],
    mutationFn: async () => {
      const response = await graphqlClient.request(ANALYZE_COMPANY_AGAINST_PATENT, {
        input: {
          patentPublicationNumber: selectedPatent.publicationNumber,
          companyName: selectedCompany.name
        }
      });
      return response.analyzeCompanyAgainstPatent;
    },
    onSuccess: (data) => {
      setAnalysisId(data.companyAnalysisId);
      toast({
        title: "Analysis Complete",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    },
    onError: (error) => {
      toast({
        title: "Analysis Failed",
        description: error.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  });

  return {
    analysisResult,
    isAnalyzing,
    isLoadingAnalysis,
    isLoading: isAnalyzing || isQueryLoading,
    runAnalysis: mutate,
    analysisId,
    refetchAnalysis
  };
}; 