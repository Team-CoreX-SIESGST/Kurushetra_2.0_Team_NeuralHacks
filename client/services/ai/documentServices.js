import { apiClient } from "@/helper/commonHelper";

/**
 * Process a single document through the complete enhanced workflow
 * Includes JSON conversion, Gemini RAG summarization, web search, and enhanced summary
 * @param {File} file - Document file to process
 * @param {string} [workspaceId] - Optional workspace identifier
 */
export const processSingleDocument = async (file, workspaceId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (workspaceId) {
    formData.append('workspace_id', workspaceId);
  }
  
  return apiClient.post("/v1/enhanced-documents/process/single", formData);
};

/**
 * Process multiple documents through the enhanced workflow with comparative analysis
 * @param {File[]} files - Array of document files (max 10)
 * @param {string} [workspaceId] - Optional workspace identifier
 */
export const processMultipleDocuments = async (files, workspaceId = null) => {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });
  
  if (workspaceId) {
    formData.append('workspace_id', workspaceId);
  }
  
  return apiClient.post("/v1/enhanced-documents/process/batch", formData);
};

/**
 * Convert a document to structured JSON format without AI processing
 * @param {File} file - Document file to convert
 */
export const convertDocumentToJSON = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post("/v1/enhanced-documents/convert/json", formData);
};

/**
 * Generate a basic document summary using Gemini RAG without web enhancement
 * @param {File} file - Document file to summarize
 */
export const generateBasicSummary = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post("/v1/enhanced-documents/summarize/basic", formData);
};

/**
 * Generate searchable tags for a document using Gemini AI
 * @param {File} file - Document file to analyze
 */
export const generateSearchTags = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post("/v1/enhanced-documents/tags/generate", formData);
};

/**
 * Extract related URLs from document processing without full enhancement
 * @param {File} file - Document file to analyze
 */
export const extractRelatedURLs = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post("/v1/enhanced-documents/urls/extract", formData);
};
