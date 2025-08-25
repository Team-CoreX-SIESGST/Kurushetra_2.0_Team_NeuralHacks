import { apiClient } from "@/helper/commonHelper";

export const getPlans = async () => {
  const response = await apiClient.get("/subscription/plans");
  return response.data;
};
export const getCurrentSubscription = async () => {
  const response = await apiClient.get("/subscription/current");
  return response.data;
};
export const subscribeToPlan = async () => {
  const response = await apiClient.post("/subscription/subscribe");
  return response.data;
};
export const getTokenUsageStats = async () => {
  const response = await apiClient.get("/subscription//usage-stats");
  return response.data;
};

