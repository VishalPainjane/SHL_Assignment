# SHL Assessment Recommendation System

This application helps hiring managers find the right assessments for their job roles.

## Features

- Accepts natural language queries, job descriptions, or job post URLs
- Returns relevant SHL assessments based on the input
- Displays recommendations in a tabular format with assessment details
- Supports filtering by test duration and other parameters
- Provides relevance scores for each recommendation

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **LLM Integration**: Google Gemini
- **Vector Search**: ChromaDB
- **Text Embeddings**: Sentence Transformers
- **Web Scraping**: BeautifulSoup

## Project Structure

- `/app` - Application code
  - `/frontend` - Streamlit web interface
  - `/backend` - FastAPI backend and recommendation engine
- `/data` - Data files
  - `/raw` - Raw scraped data
  - `/processed` - Processed assessment data
- `/models` - Vector database and model files
- `/utils` - Utility scripts including web crawler
- `config.py` - Configuration settings
- `run.py` - Main script to launch the application

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ and npm

### Installation

1. Clone this repository

2. Set up the backend:

   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd frontend
   npm install
   ```

### Running the Application

#### Backend

## API Endpoints

- `POST /api/recommend` - Get assessment recommendations
  - Request body: `{"query": "your query here", "max_results": 5}`
  - Returns recommended assessments with details and relevance scores

## Evaluation

The system is evaluated using:

- Mean Recall@3 - Proportion of relevant assessments in top 3 results
- Mean Average Precision@3 (MAP@3) - Precision considering the order of results

## License

This project is created as part of the SHL AI Intern assessment task.
