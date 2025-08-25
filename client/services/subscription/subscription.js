import { apiClient } from "@/helper/commonHelper";

export const getPlans = async () => {
  const response = await apiClient.get("/subscription/plans");
  return response.data;
};

export const getCurrentSubscription = async () => {
  const response = await apiClient.get("/subscription/current");
  return response.data;
};

export const subscribeToPlan = async (planId) => {
  const response = await apiClient.post("/subscription/subscribe", { planId });
  return response.data;
};

export const createSubscriptionOrder = async (planId) => {
  const response = await apiClient.post("/subscription/create-order", {
    planId,
  });
  return response.data;
};

export const verifySubscriptionPayment = async (paymentData) => {
  const response = await apiClient.post(
    "/subscription/verify-payment",
    paymentData
  );
  return response.data;
};

export const getTokenUsageStats = async (period = "30") => {
  const response = await apiClient.get(
    `/subscription/token-usage?period=${period}`
  );
  return response.data;
};
