import React, { useState } from 'react';
import {
  Box,
  VStack,
  Text,
  Badge,
  Button,
  useToast,
  Collapse,
  List,
  ListItem,
  ListIcon,
  Spinner,
  Radio,
  RadioGroup,
  Stack,
} from '@chakra-ui/react';
import { MdCheckCircle } from 'react-icons/md';
import axios from 'axios';

const AdvancedSearch = ({ query, onQuerySelect }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [selectedQuery, setSelectedQuery] = useState('');
  const toast = useToast();

  const analyzeQuery = async () => {
    if (!query.trim()) {
      toast({
        title: 'Please enter a query first',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/analyze-query', {
        query: query,
      });
      setAnalysis(response.data);
      setSelectedQuery(response.data.pubmed_queries[0]); // Select first query by default
    } catch (error) {
      toast({
        title: 'Error analyzing query',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    }
    setIsLoading(false);
  };

  const handleQuerySelect = () => {
    if (selectedQuery) {
      onQuerySelect(selectedQuery);
    }
  };

  return (
    <Box width="100%" p={4}>
      <Button
        onClick={analyzeQuery}
        isLoading={isLoading}
        loadingText="Analyzing..."
        colorScheme="teal"
        width="100%"
        mb={4}
      >
        Analyze Query
      </Button>

      <Collapse in={analysis !== null} animateOpacity>
        <VStack spacing={4} align="start" width="100%">
          {/* Keywords */}
          <Box width="100%">
            <Text fontWeight="bold" mb={2}>
              Keywords:
            </Text>
            <List spacing={2}>
              {analysis?.keywords.map((keyword, idx) => (
                <ListItem key={idx}>
                  <ListIcon as={MdCheckCircle} color="green.500" />
                  {keyword}
                </ListItem>
              ))}
            </List>
          </Box>

          {/* MeSH Terms */}
          <Box width="100%">
            <Text fontWeight="bold" mb={2}>
              Suggested MeSH Terms:
            </Text>
            {analysis?.mesh_terms.map((term, idx) => (
              <Badge key={idx} mr={2} mb={2} colorScheme="purple">
                {term}
              </Badge>
            ))}
          </Box>

          {/* PubMed Queries */}
          <Box width="100%">
            <Text fontWeight="bold" mb={2}>
              Optimized PubMed Queries:
            </Text>
            <RadioGroup value={selectedQuery} onChange={setSelectedQuery}>
              <Stack spacing={2}>
                {analysis?.pubmed_queries.map((query, idx) => (
                  <Radio key={idx} value={query}>
                    <Text fontSize="sm">{query}</Text>
                  </Radio>
                ))}
              </Stack>
            </RadioGroup>
          </Box>

          {/* Search Strategy */}
          <Box width="100%">
            <Text fontWeight="bold" mb={2}>
              Search Strategy:
            </Text>
            <Text fontSize="sm">{analysis?.search_strategy}</Text>
          </Box>

          <Button
            colorScheme="blue"
            onClick={handleQuerySelect}
            width="100%"
            mt={4}
          >
            Use Selected Query
          </Button>
        </VStack>
      </Collapse>

      {isLoading && (
        <Box textAlign="center" mt={4}>
          <Spinner size="xl" />
          <Text mt={2}>Analyzing your query...</Text>
        </Box>
      )}
    </Box>
  );
};

export default AdvancedSearch;
