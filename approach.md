# SHL Assessment Recommendation System: Technical Approach

## Data Acquisition & Processing

1. **Web Crawling**:

   - Used BeautifulSoup to extract assessment data from SHL's product catalog
   - Captured assessment name, URL, remote testing support, adaptive testing capabilities, duration, and type
   - Stored both raw HTML and processed structured data

2. **Data Representation**:
   - Created a structured dataset with standardized fields for each assessment
   - Implemented a vector-based representation of assessment details for semantic matching
   - Used sentence-transformers to create embeddings of assessment descriptions and capabilities

## Search & Recommendation Methodology

1. **Semantic Search with ChromaDB**:

   - Generated dense vector embeddings for each assessment using Sentence Transformers
   - Created a vector database using ChromaDB for efficient similarity search
   - Implemented nearest-neighbor search to find assessments most similar to queries

2. **LLM Integration with Google Gemini**:

   - Enhanced user queries by extracting key requirements and constraints
   - Used Gemini to parse job descriptions and extract relevant assessment criteria
   - Applied prompt engineering to transform raw queries into search-optimized formats

3. **Hybrid Ranking**:
   - Combined semantic similarity scores with constraint-based filtering
   - Applied duration filters to match time constraints in queries
   - Implemented sorting based on multiple relevance factors

## Evaluation Framework

1. **Metrics Implementation**:

   - Mean Recall@3: Measures how many relevant assessments appear in top 3 results
   - MAP@3: Evaluates both precision and ranking quality of top 3 results
   - Implemented in evaluation.py with calculation functions

2. **Test Suite**:
   - Created benchmark queries with known relevant assessments
   - Measured performance against sample queries provided in the assignment
   - Implemented automated evaluation script to track performance

## Technology Stack

- **Backend**: FastAPI for RESTful API development
- **Frontend**: Streamlit for rapid UI development
- **Vector Search**: ChromaDB for efficient similarity search
- **LLM**: Google Gemini for query understanding and enhancement
- **Embeddings**: Sentence Transformers for semantic representation
- **Data Processing**: Pandas for data manipulation
- **Web Scraping**: BeautifulSoup and Requests
- **Deployment**: Docker for containerization

## Future Improvements

1. Fine-tune embeddings specifically for HR assessment domain
2. Implement user feedback mechanism to improve recommendations over time
3. Add support for multilingual queries and job descriptions
4. Enhance the crawler with periodic updates to keep assessment data current
