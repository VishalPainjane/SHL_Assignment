import React from 'react';
import './RecommendationResults.css';

function RecommendationResults({ recommendations }) {
  return (
    <div className="recommendation-results">
      <h2>Recommended Assessments</h2>
      
      {recommendations.length === 0 ? (
        <p>No recommendations found. Please try a different query.</p>
      ) : (
        <div className="results-list">
          {recommendations.map((assessment) => (
            <div key={assessment.id} className="assessment-card">
              <h3>{assessment.name}</h3>
              <div className="assessment-details">
                <span className="duration">⏱️ {assessment.duration} minutes</span>
                <p className="description">{assessment.description}</p>
                
                <div className="skills">
                  <h4>Skills Measured:</h4>
                  <div className="skill-tags">
                    {assessment.skills_measured.map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
                
                <button className="select-button">Select This Assessment</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecommendationResults;
