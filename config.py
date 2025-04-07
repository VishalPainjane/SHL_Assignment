"""Configuration settings for the SHL Assessment Recommendation System."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API and service configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SHL_CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

# Data directories
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Application settings
MAX_RECOMMENDATIONS = 10
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DB_PATH = os.path.join(MODELS_DIR, "chroma_db")
