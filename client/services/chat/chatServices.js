import { apiClient, apiClient2 } from "@/helper/commonHelper";

export const createSection = async (payload) => {
  const response = await apiClient.post("/sections",payload);
  return response.data;
};

export const getSections = () => {
  return apiClient.get("/sections");
};

export const getSection = (sectionId) => {
  return apiClient.get(`/sections/${sectionId}`);
};

export const sendMessage = (sectionId,payload) => {
  return apiClient.post(`/sections/${sectionId}/message`,payload);
};

export const updateSectionTitle = (sectionId, payload) => {
  return apiClient.put(`/sections/${sectionId}/title`, payload);
};

export const deleteSection = (sectionId) => {
  return apiClient.delete(`/sections/${sectionId}`);
};

export const python_pdf_to_text = (file) => {
  const formData = new FormData();
  formData.append("file", file); // name must match FastAPI param

  return apiClient2.post("/process-file", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

