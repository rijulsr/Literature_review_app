import React, { useState } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Grid,
  Input,
  Button,
  Text,
  Heading,
  Container,
  Card,
  CardBody,
  Badge,
  Spinner,
  useToast,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  FormControl,
  FormLabel,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(20);
  const [filterStats, setFilterStats] = useState(true);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);

  const toast = useToast();

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: 'Please enter a search query',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/search', {
        query,
        max_results: maxResults,
        filter_stats: filterStats,
      });
      setArticles(response.data);
      
      if (response.data.length === 0) {
        toast({
          title: 'No results found',
          status: 'info',
          duration: 3000,
        });
      }
    } catch (error) {
      toast({
        title: 'Error fetching results',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    }
    setLoading(false);
  };

  return (
    <ChakraProvider>
      <Box textAlign="center" fontSize="xl" p={5}>
        <Container maxW="container.xl">
          <VStack spacing={8}>
            <Heading as="h1" size="2xl" mb={8}>
              Literature Review Assistant
            </Heading>

            <Card width="100%" p={5}>
              <CardBody>
                <VStack spacing={4}>
                  <Input
                    placeholder="Enter your research query in natural language..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    size="lg"
                  />
                  
                  <Grid templateColumns="repeat(2, 1fr)" gap={4} width="100%">
                    <FormControl>
                      <FormLabel>Max Results</FormLabel>
                      <NumberInput
                        value={maxResults}
                        onChange={(value) => setMaxResults(parseInt(value))}
                        min={1}
                        max={100}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Filter Statistical Studies</FormLabel>
                      <Switch
                        isChecked={filterStats}
                        onChange={(e) => setFilterStats(e.target.checked)}
                        size="lg"
                      />
                    </FormControl>
                  </Grid>

                  <Button
                    colorScheme="blue"
                    onClick={handleSearch}
                    isLoading={loading}
                    loadingText="Searching..."
                    size="lg"
                    width="200px"
                    mt={4}
                  >
                    Search
                  </Button>
                </VStack>
              </CardBody>
            </Card>

            {loading ? (
              <Spinner size="xl" />
            ) : (
              <VStack spacing={4} width="100%">
                {articles.map((article) => (
                  <Card key={article.pubmed_id} width="100%">
                    <CardBody>
                      <Accordion allowToggle>
                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Text fontWeight="bold" fontSize="lg">
                                {article.title}
                              </Text>
                              <Text fontSize="sm" color="gray.600">
                                {article.authors.join(', ')} • {article.journal} • {article.year}
                              </Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          
                          <AccordionPanel>
                            <VStack align="start" spacing={4}>
                              <Box>
                                <Badge colorScheme="blue" mb={2}>Abstract</Badge>
                                <Text>{article.abstract}</Text>
                              </Box>
                              
                              {article.summary && (
                                <Box>
                                  <Badge colorScheme="green" mb={2}>AI Summary</Badge>
                                  <Text>{article.summary}</Text>
                                </Box>
                              )}
                            </VStack>
                          </AccordionPanel>
                        </AccordionItem>
                      </Accordion>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            )}
          </VStack>
        </Container>
      </Box>
    </ChakraProvider>
  );
}

export default App;
