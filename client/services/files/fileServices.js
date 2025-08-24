import { apiClient } from "@/helper/commonHelper";

/**
 * Upload a file to the FastAPI backend
 * @param {File} file - The file to upload
 * @param {string} workspaceId - Workspace identifier
 * @param {string} [fileId] - Optional custom file ID
 */
export const uploadFile = async (file, workspaceId, fileId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('workspace_id', workspaceId);
  
  if (fileId) {
    formData.append('file_id', fileId);
  }
  
  return apiClient.post("/v1/upload", formData);
};

/**
 * Get upload status for a specific file
 * @param {string} fileId - File identifier
 * @param {string} workspaceId - Workspace identifier
 */
export const getUploadStatus = async (fileId, workspaceId) => {
  return apiClient.get(`/v1/upload/status/${fileId}?workspace_id=${workspaceId}`);
};

/**
 * Delete an uploaded file
 * @param {string} fileId - File identifier
 * @param {string} workspaceId - Workspace identifier
 */
export const deleteUploadedFile = async (fileId, workspaceId) => {
  return apiClient.delete(`/v1/upload/${fileId}?workspace_id=${workspaceId}`);
};

/**
 * Get file information and metadata
 * @param {string} fileId - File identifier
 * @param {string} workspaceId - Workspace identifier
 */
export const getFileInfo = async (fileId, workspaceId) => {
  return apiClient.get(`/v1/file/${fileId}?workspace_id=${workspaceId}`);
};

/**
 * Download a file
 * @param {string} fileId - File identifier
 * @param {string} workspaceId - Workspace identifier
 */
export const downloadFile = async (fileId, workspaceId) => {
  return apiClient.get(`/v1/file/${fileId}/download?workspace_id=${workspaceId}`);
};

/**
 * Get comprehensive metadata for a file
 * @param {string} fileId - File identifier
 * @param {string} workspaceId - Workspace identifier
 */
export const getFileMetadata = async (fileId, workspaceId) => {
  return apiClient.get(`/v1/file/${fileId}/metadata?workspace_id=${workspaceId}`);
};

/**
 * Batch upload multiple files
 * @param {File[]} files - Array of files to upload
 * @param {string} workspaceId - Workspace identifier
 */
export const batchUploadFiles = async (files, workspaceId) => {
  const uploadPromises = files.map(file => uploadFile(file, workspaceId));
  return Promise.allSettled(uploadPromises);
};

/**
 * Get workspace file statistics
 * @param {string} workspaceId - Workspace identifier
 */
export const getWorkspaceStats = async (workspaceId) => {
  // This would need to be implemented in the backend
  return apiClient.get(`/v1/workspace/${workspaceId}/stats`);
};
