import axios from 'axios';

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
      await axios.get(`${API_BASE_URL}/api/health`);
    } catch (healthError) {
      throw new Error('API server is not running. Please start the backend server.');
    }
    
    // Proceed with the actual recommendation request
    const response = await axios.post(`${API_BASE_URL}/api/recommend`, {
      query_type: queryType,
      query: query,
      max_results: maxResults
    });
    
    return response.data;
  } catch (error) {
    console.error('API request failed:', error);
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get recommendations');
  }
}
