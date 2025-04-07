from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    query_type: str  # "natural_language", "job_description", or "url"
    query: str
    max_results: int = 10

class Assessment(BaseModel):
    id: str
    name: str
    duration: int  # in minutes
    description: str
    skills_measured: List[str]

@app.post("/api/recommend", response_model=List[Assessment])
async def recommend_assessments(request: RecommendationRequest):
    """Generate assessment recommendations based on the input query."""
    try:
        # Mock data for demonstration purposes
        # In a real application, this would use ML or a database lookup
        sample_assessments = [
            Assessment(
                id="java001",
                name="Java Programming Assessment",
                duration=30,
                description="Evaluates core Java programming skills including syntax, OOP concepts, and problem-solving.",
                skills_measured=["Java", "OOP", "Problem Solving"]
            ),
            Assessment(
                id="collab001",
                name="Business Collaboration Skills",
                duration=20,
                description="Assesses ability to communicate effectively with business stakeholders.",
                skills_measured=["Communication", "Collaboration", "Business Acumen"]
            )
        ]
        
        # Filter by search terms - simple implementation
        if "java" in request.query.lower():
            results = [a for a in sample_assessments if "java" in a.name.lower()]
        else:
            results = sample_assessments
            
        # Limit results
        return results[:request.max_results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
