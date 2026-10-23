import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000, // 45s for deep AI reasoning
});

export const apiService = {
  // Check backend health
  async checkHealth() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.warn('Backend health check error:', error);
      return { status: 'offline', error: error.message };
    }
  },

  // Full AI Code Review
  async submitReview({ code, language, problemTitle, problemDescription, testCases }) {
    const payload = {
      code,
      language,
      problemTitle,
      problemDescription,
      testCases: (testCases || []).map(tc => ({
        input: tc.input || '',
        expectedOutput: tc.expectedOutput || tc.expected_output || ''
      }))
    };
    const response = await apiClient.post('/reviews', payload);
    return response.data;
  },

  // Sandbox: Run single snippet against custom input
  async runSingle({ code, language, input }) {
    const payload = { code, language, input };
    const response = await apiClient.post('/runner/run-single', payload);
    return response.data;
  },

  // Sandbox: Run batch test cases
  async runBatchTests({ code, language, testCases }) {
    const payload = { code, language, testCases };
    const response = await apiClient.post('/runner/run-tests', payload);
    return response.data;
  },

  // Fetch recent reviews history
  async getRecentReviews() {
    const response = await apiClient.get('/reviews');
    return response.data;
  }
};
