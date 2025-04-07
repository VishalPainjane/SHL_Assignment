# SHL Assessment Analysis

This project analyzes SHL assessment data to provide insights into various assessment types, their characteristics, and applications.

## Project Overview

This repository contains code and data for analyzing SHL assessments, which are widely used for pre-employment screening and talent evaluation. The analysis includes processing raw assessment data, transforming it into structured formats, and extracting meaningful insights.

## Dataset

The project uses two main data sources:

- `data/raw/shl_catalog_raw.json`: Raw data from the SHL catalog containing detailed information about various assessments
- `data/processed/shl_assessments.csv`: Processed assessment data with standardized fields including:
  - Assessment name
  - URL
  - Remote testing availability
  - Adaptive IRT support
  - Test types (A, B, P, S)
  - Solution type
  - Description
  - Duration
  - Languages
  - Job levels
  - Assessment length

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

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
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
