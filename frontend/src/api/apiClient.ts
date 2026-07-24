import axios from 'axios';

// Create base instance
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // Important for sending/receiving the refresh cookie
});

// Interceptor to attach access token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    if (config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // append the token as a query parameter for get_current_user
    config.params = { ...config.params, access: token };
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Interceptor to handle 401s and refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh the token
        const response = await axios.post(
          'http://localhost:8000/auth/refresh',
          {},
          { withCredentials: true }
        );
        
        const { access_token } = response.data;
        
        // Save new token
        localStorage.setItem('access_token', access_token);
        
        // Update header and retry original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
        
      } catch (refreshError) {
        // Refresh failed (e.g. refresh token expired or missing)
        localStorage.removeItem('access_token');
        // Optional: emit an event or call a function to log out globally
        window.dispatchEvent(new Event('auth:unauthorized'));
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
