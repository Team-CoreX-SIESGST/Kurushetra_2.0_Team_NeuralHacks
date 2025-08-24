import { apiClient } from "@/helper/commonHelper";

/**
 * Perform AI-powered search using Gemini RAG pipeline
 * @param {Object} searchRequest - Search parameters
 * @param {string} searchRequest.workspace_id - Workspace identifier
 * @param {string} searchRequest.query - Search query
 * @param {number} [searchRequest.top_k=10] - Maximum number of results
 * @param {boolean} [searchRequest.include_web=true] - Include web search results
 * @param {boolean} [searchRequest.summarize=true] - Generate summary
 */
export const performAISearch = async (searchRequest) => {
  return apiClient.post("/v1/search", searchRequest);
};

/**
 * Perform simple AI search without web enhancement
 * @param {string} workspaceId - Workspace identifier
 * @param {string} query - Search query
 * @param {number} [topK=5] - Maximum number of results
 */
export const performSimpleSearch = async (workspaceId, query, topK = 5) => {
  return apiClient.get(`/v1/search/simple?workspace_id=${workspaceId}&query=${encodeURIComponent(query)}&top_k=${topK}`);
};

/**
 * Get search statistics for a workspace
 * @param {string} workspaceId - Workspace identifier
 */
export const getSearchStats = async (workspaceId) => {
  return apiClient.get(`/v1/search/stats/${workspaceId}`);
};
