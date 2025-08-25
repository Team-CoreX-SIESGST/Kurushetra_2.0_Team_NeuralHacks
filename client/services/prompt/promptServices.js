import { apiClient } from "@/helper/commonHelper";


export const improvePrompt = () => {
  return apiClient.post(`/ai/improve`);
};
export const suggestPromptStructure = () => {
  return apiClient.post(`/ai//suggest-structure`);
};

