import { apiClient } from "@/helper/commonHelper";

/**
 * Register a new user with the FastAPI backend
 * Uses form data for file uploads (profile image)
 * @param {Object} userData - User registration data
 * @param {string} userData.name - User's full name
 * @param {string} userData.phone - User's phone number
 * @param {string} userData.pin - User's PIN (password)
 * @param {string} userData.role - User's role (default: 'user')
 * @param {File} [userData.image] - Optional profile image
 */
export const registerUser = async (userData) => {
  const formData = new FormData();
  formData.append('name', userData.name);
  formData.append('phone', userData.phone);
  formData.append('pin', userData.pin);
  formData.append('role', userData.role || 'user');
  
  // Add image if provided
  if (userData.image) {
    formData.append('image', userData.image);
  }
  
  return apiClient.post("/register", formData);
};

/**
 * Login user with phone number and PIN
 * @param {Object} credentials
 * @param {string} credentials.phone - User's phone number
 * @param {string} credentials.pin - User's PIN
 */
export const loginUser = async (credentials) => {
  const formData = new FormData();
  formData.append('phone', credentials.phone);
  formData.append('pin', credentials.pin);
  
  return apiClient.post("/login", formData);
};

/**
 * Test the user authentication endpoint
 */
export const testUserRoute = async () => {
  return apiClient.get("/test");
};

