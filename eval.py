"""Evaluation script for the SHL Assessment Recommendation System."""
import os
import json
import numpy as np
from typing import List, Dict, Any
import pandas as pd
import importlib
from app import RecommendationSystem

# Path to the data file
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "data", "processed")
ASSESSMENTS_PATH = r"C:\Users\nikhi\OneDrive\Documents\GitHub\SHL_Assignment\data\processed\shl_test_solutions.csv"

# Test queries with ground truth relevant assessments
# In a real scenario, you would have a proper evaluation dataset with human-labeled relevance
TEST_QUERIES = [
    {
        "query": "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes.",
        "relevant_assessments": ["Java", "Core Java", "Java Spring Boot", "Java Programming", "Collaboration Skills"],
        "time_constraint": 40
    },
    {
        "query": "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script. Need an assessment package that can test all skills with max duration of 60 minutes.",
        "relevant_assessments": ["Python", "SQL", "JavaScript", "Full Stack Developer", "Web Development"],
        "time_constraint": 60
    },
    {
        "query": "I am hiring for an analyst and wants applications to screen using Cognitive and personality tests, what options are available within 45 mins.",
        "relevant_assessments": ["Analytical Thinking", "Cognitive Ability", "Personality", "Decision Making", "Data Analysis"],
        "time_constraint": 45
    }
]

def is_relevant(assessment: Dict[str, Any], relevant_keywords: List[str]) -> bool:
    """
    Check if an assessment is relevant based on keywords in its name or description
    
    Args:
        assessment: Assessment dictionary with 'name' and optionally 'description'
        relevant_keywords: List of keywords to match against
    
    Returns:
        Boolean indicating relevance
    """
    assessment_name = assessment["name"].lower()
    assessment_desc = assessment.get("description", "").lower() if isinstance(assessment.get("description", ""), str) else ""
    
    # Special case for cognitive/personality assessments
    if any(kw.lower() in ["cognitive ability", "personality", "analytical thinking"] for kw in relevant_keywords):
        cognitive_keywords = ["reasoning", "cognitive", "numerical", "verbal", "inductive", "deductive", "verify"]
        personality_keywords = ["personality", "trait", "behavior", "opq"]
        analytical_keywords = ["analytical", "analysis", "problem solving", "critical thinking"]
        
        # Check if assessment name contains any cognitive/personality keywords
        if any(kw in assessment_name for kw in cognitive_keywords + personality_keywords + analytical_keywords):
            return True
        if assessment_desc and any(kw in assessment_desc for kw in cognitive_keywords + personality_keywords + analytical_keywords):
            return True
    
    # General keyword matching
    for keyword in relevant_keywords:
        keyword_lower = keyword.lower()
        
        # Direct match in name or description
        if keyword_lower in assessment_name or (assessment_desc and keyword_lower in assessment_desc):
            return True
        
        # Word boundary matching to avoid partial word matches
        name_words = assessment_name.split()
        for word in name_words:
            # Allow stemming-like matching (e.g. 'Python' matches 'Python-based')
            if (keyword_lower in word or word in keyword_lower) and len(word) >= 4 and len(keyword_lower) >= 4:
                return True
                
        # Try matching in description
        if assessment_desc:
            desc_words = assessment_desc.split()
            for word in desc_words:
                if (keyword_lower in word or word in keyword_lower) and len(word) >= 4 and len(keyword_lower) >= 4:
                    return True
    
    return False

def precision_at_k(recommended: List[Dict[str, Any]], relevant_keywords: List[str], k: int) -> float:
    """Calculate precision@k"""
    if k == 0 or not recommended:
        return 0.0
    
    hits = sum(1 for i, item in enumerate(recommended[:k]) 
              if is_relevant(item, relevant_keywords))
    return hits / k

def recall_at_k(recommended: List[Dict[str, Any]], relevant_keywords: List[str], k: int) -> float:
    """Calculate recall@k"""
    if not relevant_keywords or not recommended:
        return 0.0
    
    hits = sum(1 for i, item in enumerate(recommended[:k]) 
              if is_relevant(item, relevant_keywords))
    return hits / len(relevant_keywords)

def average_precision(recommended: List[Dict[str, Any]], relevant_keywords: List[str], k: int) -> float:
    """Calculate average precision@k"""
    if not recommended or not relevant_keywords:
        return 0.0
    
    precisions = []
    num_relevant_found = 0
    
    for i in range(min(k, len(recommended))):
        if is_relevant(recommended[i], relevant_keywords):
            num_relevant_found += 1
            precisions.append(num_relevant_found / (i + 1))
    
    if not precisions:
        return 0.0
    
    return sum(precisions) / min(len(relevant_keywords), k)

def evaluate_system():
    """Evaluate the recommendation system using test queries"""
    # Load data before creating recommender to avoid double initialization
    assessments_df = pd.read_csv(ASSESSMENTS_PATH)
    
    # Now create recommendation system with the pre-loaded data
    print("Initializing recommendation system...")
    recommender = RecommendationSystem(ASSESSMENTS_PATH)
    
    recalls = []
    avg_precisions = []
    
    print("\n=== Evaluation Results ===")
    
    for i, test_case in enumerate(TEST_QUERIES):
        query = test_case["query"]
        relevant_keywords = test_case["relevant_assessments"]
        
        print(f"\nQuery {i+1}: {query}")
        print(f"Relevant assessment keywords: {relevant_keywords}")
        
        # Get recommendations
        recommendations = recommender.recommend(query, max_results=10)
        
        # Display enhanced query if available in the recommendation response
        if hasattr(recommender, 'enhanced_query') and recommender.enhanced_query:
            print(f"Original query: {query}")
            print(f"Enhanced query: {recommender.enhanced_query}")
        
        # Fix the "minutes minutes" issue by checking and cleaning the duration format
        print("\nTop 3 Recommendations:")
        for j, rec in enumerate(recommendations[:3]):
            # Fix duration formatting - remove the word "minutes" if it's already in the rec['duration']
            duration_str = str(rec['duration'])
            if "minute" not in duration_str.lower():
                duration_display = f"{duration_str} minutes"
            else:
                duration_display = duration_str
                
            relevance_marker = "✓" if is_relevant(rec, relevant_keywords) else " "
            print(f"{j+1}. {rec['name']} (Duration: {duration_display}, Score: {rec['similarity_score']:.2f}) {relevance_marker}")
        
        # Calculate metrics at k=3
        k = 3
        recall = recall_at_k(recommendations, relevant_keywords, k)
        ap = average_precision(recommendations, relevant_keywords, k)
        
        recalls.append(recall)
        avg_precisions.append(ap)
        
        print(f"\nMetrics at k={k}:")
        print(f"Recall@{k}: {recall:.2f}")
        print(f"AP@{k}: {ap:.2f}")
        
        # Debug information about relevance matching
        print("\nRelevance details:")
        for j, rec in enumerate(recommendations[:k]):
            is_rel = is_relevant(rec, relevant_keywords)
            print(f"- {rec['name']}: {'Relevant' if is_rel else 'Not relevant'}")
    
    # Calculate mean metrics
    mean_recall = np.mean(recalls)
    mean_ap = np.mean(avg_precisions)
    
    print("\n=== Overall Performance ===")
    print(f"Mean Recall@3: {mean_recall:.4f}")
    print(f"MAP@3: {mean_ap:.4f}")

# Prevent RecommendationSystem from being imported twice
if __name__ == "__main__":
    evaluate_system()


