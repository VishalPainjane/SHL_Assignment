import React, { useState } from 'react';
import './RecommendationForm.css';

function RecommendationForm({ onSubmit, isLoading }) {
  const [inputType, setInputType] = useState('job_description');
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(5);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      inputType,
      query,
      maxResults
    });
  };
  
  return (
    <div className="recommendation-form">
      <h2>Input Query</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Select input type:</label>
          <div className="input-types">
            <button 
              type="button"
              className={inputType === 'natural_language' ? 'active' : ''}
              onClick={() => setInputType('natural_language')}
            >
              Natural Language Query
            </button>
            <button
              type="button"
              className={inputType === 'job_description' ? 'active' : ''}
              onClick={() => setInputType('job_description')}
            >
              Job Description
            </button>
            <button
              type="button"
              className={inputType === 'url' ? 'active' : ''}
              onClick={() => setInputType('url')}
            >
              Job Post URL
            </button>
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="query">
            {inputType === 'natural_language' ? 'Enter your query:' : 
             inputType === 'job_description' ? 'Enter job description:' : 
             'Enter job post URL:'}
          </label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              inputType === 'natural_language' ? 'e.g., Find assessments for Java developers with good communication skills' : 
              inputType === 'job_description' ? 'Paste job description here...' : 
              'Paste job posting URL here...'
            }
            rows={5}
            required
          ></textarea>
        </div>
        
        <div className="form-group">
          <label>Maximum number of recommendations:</label>
          <div className="max-results">
            <button 
              type="button" 
              className={maxResults === 1 ? 'active' : ''}
              onClick={() => setMaxResults(1)}
            >1</button>
            <button 
              type="button" 
              className={maxResults === 3 ? 'active' : ''}
              onClick={() => setMaxResults(3)}
            >3</button>
            <button 
              type="button" 
              className={maxResults === 5 ? 'active' : ''}
              onClick={() => setMaxResults(5)}
            >5</button>
            <button 
              type="button" 
              className={maxResults === 10 ? 'active' : ''}
              onClick={() => setMaxResults(10)}
            >10</button>
          </div>
        </div>
        
        <button type="submit" className="submit-btn" disabled={isLoading}>
          {isLoading ? 'Getting Recommendations...' : 'Get Recommendations'}
        </button>
      </form>
      
      <div className="example-queries">
        <h3>Example Queries</h3>
        <ul>
          <li onClick={() => setQuery('Java developers who can also collaborate with business teams')}>
            Java developers who can also collaborate with business teams
          </li>
          <li onClick={() => setQuery('Frontend developer with React and accessibility experience')}>
            Frontend developer with React and accessibility experience
          </li>
          <li onClick={() => setQuery('Data scientist with expertise in NLP and machine learning')}>
            Data scientist with expertise in NLP and machine learning
          </li>
        </ul>
      </div>
    </div>
  );
}

export default RecommendationForm;
