"""
Main script to launch the SHL Assessment Recommendation System.
This script starts both the backend API and frontend Streamlit app.
"""
import os
import sys
import subprocess
import time
import webbrowser
from threading import Thread

def create_directory_structure():
    """Create the necessary directory structure and placeholder files."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create directories with absolute paths
    for directory in ["data/raw", "data/processed", "models", "app/backend", "app/frontend"]:
        os.makedirs(os.path.join(current_dir, directory), exist_ok=True)
    
    # Create placeholder API file if it doesn't exist
    api_file = os.path.join(current_dir, "app", "backend", "api.py")
    if not os.path.exists(api_file):
        with open(api_file, "w") as f:
            f.write("""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="SHL Assessment Recommendation API")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
""")
    
    # Create placeholder frontend file if it doesn't exist
    frontend_file = os.path.join(current_dir, "app", "frontend", "app.py")
    if not os.path.exists(frontend_file):
        with open(frontend_file, "w") as f:
            f.write("""
import streamlit as st

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("🧠 SHL Assessment Recommendation System")
st.info("This is a placeholder. The complete application is currently being built.")

st.write("Enter a natural language query, job description, or job post URL to get started.")
query = st.text_area("Query:", height=100)

if st.button("Get Recommendations"):
    st.warning("Backend API connection not configured yet.")
""")

def run_api():
    """Run the FastAPI backend."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(current_dir, "app", "backend")
    os.chdir(backend_dir)
    subprocess.run([sys.executable, "api.py"])

def run_frontend():
    """Run the Streamlit frontend."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(current_dir, "app", "frontend")
    os.chdir(frontend_dir)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def main():
    """Main function to start the application."""
    print("Starting SHL Assessment Recommendation System...")
    
    # Create necessary directories and placeholder files
    create_directory_structure()
    
    # Start API in a separate thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Wait for API to start
    print("Waiting for API to start...")
    time.sleep(5)
    
    # Open web browser with the Streamlit app
    print("Opening Streamlit app in web browser...")
    webbrowser.open("http://localhost:8501")
    
    # Start frontend
    run_frontend()

if __name__ == "__main__":
    main()
