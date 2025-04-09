import os
import re
import numpy as np
from typing import List, Dict, Any, Optional
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="API for recommending SHL assessments based on job descriptions or queries",
    version="1.0.0"
)

# Path to the data file
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data", "processed")
# ASSESSMENTS_PATH = os.path.join(DATA_DIR, "shl_test_solutions.csv")
ASSESSMENTS_PATH = os.path.join(ROOT_DIR, "data", "processed", "shl_test_solutions.csv")

# ASSESSMENTS_PATH = r"data\processed\shl_test_solutions.csv"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
# Load and prepare data
class RecommendationSystem:
    def __init__(self, data_path: str):
        self.df = pd.read_csv(data_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Clean and prepare data
        self.prepare_data()
        
        # Create embeddings
        self.create_embeddings()
        
        # Initialize Gemini model for query enhancement
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    
    def prepare_data(self):
        """Clean and prepare the assessment data"""
        # Ensure all text columns are strings
        text_cols = ['name', 'description', 'job_levels', 'test_types_expanded']
        for col in text_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('').astype(str)
        
        # Extract duration in minutes as numeric value
        self.df['duration_minutes'] = self.df['duration'].apply(
            lambda x: int(re.search(r'(\d+)', str(x)).group(1)) 
            if isinstance(x, str) and re.search(r'(\d+)', str(x)) 
            else 60  # Default value
        )
    
    def create_embeddings(self):
        """Create embeddings for assessments"""
        # Create rich text representation for each assessment
        self.df['combined_text'] = self.df.apply(
            lambda row: f"Assessment: {row['name']}. "
                       f"Description: {row['description']}. "
                       f"Job Levels: {row['job_levels']}. "
                       f"Test Types: {row['test_types_expanded']}. "
                       f"Duration: {row['duration']}.",
            axis=1
        )
        
        # Generate embeddings
        print("Generating embeddings for assessments...")
        self.embeddings = self.model.encode(self.df['combined_text'].tolist())
        
        # Create FAISS index for fast similarity search
        self.dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(self.embeddings).astype('float32'))
        print(f"Created FAISS index with {len(self.df)} assessments")
    
    def enhance_query(self, query: str) -> str:
        """Use Gemini to enhance the query with assessment-relevant terms"""
        prompt = f"""
        I need to find SHL assessments based on this query: "{query}"
        
        Please reformulate this query to include specific skills, job roles, and assessment criteria 
        that would help in finding relevant technical assessments. Focus on keywords like programming 
        languages, technical skills, job levels, and any time constraints mentioned.
        
        Return only the reformulated query without any explanations or additional text.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            enhanced_query = response.text.strip()
            print(f"Original query: {query}")
            print(f"Enhanced query: {enhanced_query}")
            return enhanced_query
        except Exception as e:
            print(f"Error enhancing query with Gemini: {e}")
            return query  # Return original query if enhancement fails
    
    def parse_duration_constraint(self, query: str) -> Optional[int]:
        """Extract duration constraint from query"""
        # Look for patterns like "within 45 minutes", "less than 30 minutes", etc.
        patterns = [
            r"(?:within|in|under|less than|no more than)\s+(\d+)\s+(?:min|mins|minutes)",
            r"(\d+)\s+(?:min|mins|minutes)(?:\s+(?:or less|max|maximum|limit))",
            r"(?:max|maximum|limit)(?:\s+(?:of|is))?\s+(\d+)\s+(?:min|mins|minutes)",
            r"(?:time limit|duration)(?:\s+(?:of|is))?\s+(\d+)\s+(?:min|mins|minutes)",
            r"(?:completed in|takes|duration of)\s+(\d+)\s+(?:min|mins|minutes)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def recommend(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Recommend assessments based on query"""
        # Enhance query using Gemini
        enhanced_query = self.enhance_query(query)
        
        # Extract duration constraint if any
        duration_limit = self.parse_duration_constraint(query)
        
        # Generate embedding for the query
        query_embedding = self.model.encode([enhanced_query])
        
        # Search for similar assessments
        D, I = self.index.search(np.array(query_embedding).astype('float32'), len(self.df))
        
        # Get the indices of the most similar assessments
        indices = I[0]
        
        # Apply duration filter if specified
        if duration_limit:
            filtered_indices = [
                idx for idx in indices 
                if self.df.iloc[idx]['duration_minutes'] <= duration_limit
            ]
            indices = filtered_indices if filtered_indices else indices
        
        # Prepare results, limiting to max_results
        results = []
        for idx in indices[:max_results]:
            assessment = self.df.iloc[idx]
            results.append({
                "name": assessment["name"],
                "url": assessment["url"],
                "remote_testing": assessment["remote_testing"],
                "adaptive_irt": assessment["adaptive_irt"],
                "duration": assessment["duration"],
                "test_types": assessment["test_types"],
                "test_types_expanded": assessment["test_types_expanded"],
                "description": assessment["description"],
                "job_levels": assessment["job_levels"],
                "similarity_score": float(1.0 - (D[0][list(indices).index(idx)] / 100))  # Normalize to 0-1
            })
        
        return results

# Initialize the recommendation system
try:
    recommender = RecommendationSystem(ASSESSMENTS_PATH)
    print("Recommendation system initialized successfully")
except Exception as e:
    print(f"Error initializing recommendation system: {e}")
    recommender = None

# Define API response model
class AssessmentRecommendation(BaseModel):
    name: str
    url: str
    remote_testing: str
    adaptive_irt: str
    duration: str
    test_types: str
    test_types_expanded: str
    description: str
    job_levels: str
    similarity_score: float

class RecommendationResponse(BaseModel):
    query: str
    enhanced_query: str
    recommendations: List[AssessmentRecommendation]

# Define API endpoints
@app.get("/", response_model=dict)
def root():
    """Root endpoint that returns API information"""
    return {
        "name": "SHL Assessment Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "/recommend": "GET endpoint for assessment recommendations"
        }
    }

@app.get("/recommend", response_model=RecommendationResponse)
def recommend(
    query: str = Query(..., description="Natural language query or job description text"),
    max_results: int = Query(10, ge=1, le=10, description="Maximum number of results to return")
):
    """Recommend SHL assessments based on query"""
    if not recommender:
        raise HTTPException(
            status_code=500, 
            detail="Recommendation system not initialized properly"
        )
    
    # Get enhanced query for transparency
    enhanced_query = recommender.enhance_query(query)
    
    # Get recommendations
    recommendations = recommender.recommend(query, max_results=max_results)
    
    return {
        "query": query,
        "enhanced_query": enhanced_query,
        "recommendations": recommendations
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)