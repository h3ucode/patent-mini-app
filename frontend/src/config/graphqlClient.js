import { QueryClient } from '@tanstack/react-query';
import { GraphQLClient } from 'graphql-request';

export const queryClient = new QueryClient();
export const graphqlClient = new GraphQLClient('http://localhost:8000/graphql'); 