import { apiClient } from "@/helper/commonHelper";

export const getTrendingProducts = async () => {
  const response = await apiClient.get("/product/trend");
  return response.data;
};

export const registerUser = (data) => {
  return apiClient.post("/users/create", data);
};

export const loginUser = (payload) =>{
  return apiClient.post("/users/login",payload);
}

