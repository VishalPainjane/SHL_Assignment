# SHL Assessment Recommendation System

## 📋 Overview
This intelligent recommendation system helps hiring managers find the right SHL assessments for their roles. The system translates natural language queries into precise assessment recommendations, streamlining the recruitment process.

### Web Interface
**Live Website**: [https://shl-live-phli.vercel.app/](https://shl-live-phli.vercel.app/)

*GitHub*: [https://github.com/VishalPainjane/SHL_web](https://github.com/VishalPainjane/SHL_web)

### API
**Live Demo:** [https://vishalpainjane-shl-assignment.hf.space/](https://vishalpainjane-shl-assignment.hf.space/)  
**API Documentation:** [https://vishalpainjane-shl-assignment.hf.space/docs#/default/recommend_recommend_get](https://vishalpainjane-shl-assignment.hf.space/docs#/default/recommend_recommend_get)

## 🔍 Features
- Natural language query processing
- Job description analysis
- Duration and test type constraint handling
- Semantic search with vector embeddings
- LLM-enhanced query understanding
- Ranked assessment recommendations

## 📐 System Architecture & Data Flow

### Three-Tier Architecture
- **Data Layer:** Manages assessment repository and vector embeddings storage
- **Logic Layer:** Houses recommendation engine, query processing, semantic search, and filtering
- **Presentation Layer:** Provides RESTful API and web interface

### Data Flow Pipeline
1. **Query Input:** User submits natural language query
2. **Query Enhancement:** Extracts implicit meanings using Gemini API
3. **Constraint Extraction:** Identifies requirements like duration limits
4. **Semantic Search:** Uses vector similarity to find relevant assessments
5. **Post-Processing:** Applies rule-based filters and scoring
6. **Result Ranking:** Returns top-ranked assessments

## 🧠 Technical Implementation

### Data Acquisition & Processing
- **Web Scraping:** Custom scraper for SHL product catalog
- **Data Preprocessing:** 
  - Text normalization
  - Entity recognition
  - Standardization (e.g., converting durations to minutes)
- **Mock Data Generator:** For offline development

### Vector-Based Semantic Search
- **Embedding Model:** all-MiniLM-L6-v2 from Sentence Transformers
- **Storage:** FAISS index for optimized similarity search
- **Matching:** Cosine similarity for nearest-neighbor retrieval

### LLM-Enhanced Query Understanding
- **Gemini API Integration:** Extracts skills, traits, and constraints
- **Query Modes:** 
  - Expansion Mode: Broadens scope with synonyms
  - Focused Mode: Extracts key needs for precision
- **Constraint Handling:** Both explicit and implicit constraints

### Evaluation System
- **Metrics:** Mean Recall@K and Mean Average Precision@K (MAP@K)
- **Test Suite:** 50+ curated queries with expert-verified ground truth

## 🛠️ Technical Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Query Intent Disambiguation | Classified query types with specialized handling |
| Duration Constraint Extraction | Combined regex with semantic parsing |
| Cold Start Problem | Used expert-generated synthetic data |
| Vector Search Latency | Switched to HNSW indexing in FAISS |
| Precision vs. Recall Trade-off | Added dynamic similarity thresholding |

## 🚀 Usage

### API Endpoint
```
GET /recommend?query={query}&max_results={max_results}
```

**Parameters:**
- `query`: Natural language query or job description text
- `max_results`: Maximum number of results to return (default: 10)

**Example Request:**
```
GET /recommend?query=Looking for a leadership assessment for managers that can be completed in 30 minutes&max_results=3
```

## 📦 Installation

### Prerequisites
- Python 3.9+
- Required packages:
  - FastAPI
  - Sentence-Transformers
  - FAISS
  - Pandas
  - Google Generative AI

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/SHL_Assignment.git
cd SHL_Assignment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file with:
GEMINI_API_KEY=your_gemini_api_key
```

4. Run the application:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Project Structure
```
SHL_Assignment/
│
├── data/
│   ├── raw/                # Raw data files
│   │   ├── test_solutions_raw_complete.json
│   │   └── test_solutions_raw_partial.json
│   │
│   └── processed/          # Processed data files
│       ├── shl_assessments.csv
│       └── shl_test_solutions.csv
│
├── utils/                  # Utility functions
│   └── c1.py               # Web scraping and data processing
│
├── app.py                  # FastAPI application
├── config.py               # Configuration settings
├── eval.py                 # Evaluation script
├── README.md               # Project documentation
└── requirements.txt        # Dependencies
```

## 📋 Evaluation Results

The system achieves:
- Mean Recall@3: 0.85
- MAP@3: 0.78

## 🔗 References
- [SHL Product Catalog](https://www.shl.com/solutions/products/product-catalog/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Google Generative AI](https://ai.google.dev/)
