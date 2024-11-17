export const GET_PATENTS = `
  query SearchPatents($query: String, $limit: Int) {
    searchPatents(query: $query, limit: $limit) {
      patentId
      publicationNumber
      title
    }
  }
`;

export const GET_COMPANIES = `
  query GetCompanies {
    companies {
      companyId
      name
    }
  }
`;

export const ANALYZE_COMPANY_AGAINST_PATENT = `
  mutation AnalyzeCompanyAgainstPatent($input: AnalyzeCompanyAgainstPatentInput!) {
    analyzeCompanyAgainstPatent(input: $input) {
      companyId
      companyAnalysisId
      patentId
      overallRiskAssessment
      overallRisk
    }
  }
`;

export const GET_COMPANY_ANALYSIS = `
  query GetCompanyAnalysis($companyAnalysisId: String!) {
    companyAnalysis(companyAnalysisId: $companyAnalysisId) {
      companyAnalysisId
      company {
        companyId
        name
      }
      overallRisk
      overallRiskAssessment
      productAnalyses {
        edges {
          node {
            infringementLikelihood
            explanation
            specificFeaturesList
            relevantClaimsList
            product {
              name
              description
            }
          }
        }
      }
    }
  }
`;

export const TOGGLE_SAVE_ANALYSIS = `
  mutation ToggleSaveAnalysis($companyAnalysisId: String!, $isSaved: Boolean!) {
    toggleSaveAnalysis(companyAnalysisId: $companyAnalysisId, isSaved: $isSaved) {
      companyAnalysisId
      isSaved
    }
  }
`;

export const GET_SAVED_ANALYSES = `
  query GetSavedAnalyses {
    savedAnalyses {
      companyAnalysisId
      company {
        companyId
        name
      }
      patent {
        publicationNumber
        title
      }
      overallRisk
      overallRiskAssessment
      createdAt
      isSaved
      isSavedAt
      overallRisk
      overallRiskAssessment
      productAnalyses {
        edges {
          node {
            infringementLikelihood
            explanation
            specificFeaturesList
            relevantClaimsList
            product {
              name
              description
            }
          }
        }
      }
    }
  }
`; 