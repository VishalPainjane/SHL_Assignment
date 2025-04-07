import React, { useState } from 'react';
import './App.css';
import RecommendationForm from './components/RecommendationForm';
import RecommendationResults from './components/RecommendationResults';
import { getRecommendations } from './api';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  
  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    
    try {
      const results = await getRecommendations(
        formData.inputType,
        formData.query,
        formData.maxResults
      );
      setRecommendations(results);
    } catch (err) {
      setError(`${err.message}. Please ensure the backend API server is running at http://localhost:8000.`);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 SHL Assessment Recommendation System</h1>
        <p>
          This application helps hiring managers find the right assessments for their job roles.
        </p>
      </header>
      
      <main className="App-main">
        <RecommendationForm onSubmit={handleSubmit} isLoading={loading} />
        
        {error && (
          <div className="error-container">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}
        
        {!error && recommendations.length > 0 && (
          <RecommendationResults recommendations={recommendations} />
        )}
      </main>
    </div>
  );
}

export default App;
