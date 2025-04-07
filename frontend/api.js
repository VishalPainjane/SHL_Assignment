const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetches assessment recommendations from the API
 * @param {string} queryType - Type of query ("natural_language", "job_description", "url")
 * @param {string} query - The actual query text
 * @param {number} maxResults - Maximum number of results to return
 * @returns {Promise} Promise that resolves with recommendations or rejects with error
 */
export async function getRecommendations(queryType, query, maxResults = 10) {
  try {
    // First try to check if the API is available
    try {
      const healthCheck = await fetch(`${API_BASE_URL}/api/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!healthCheck.ok) {
        throw new Error('API server is not responding correctly');
      }
    } catch (healthError) {
      throw new Error('API server is not running. Please start the backend server.');
    }
    
    // Proceed with the actual recommendation request
    const response = await fetch(`${API_BASE_URL}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_type: queryType,
        query: query,
        max_results: maxResults
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get recommendations');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}
