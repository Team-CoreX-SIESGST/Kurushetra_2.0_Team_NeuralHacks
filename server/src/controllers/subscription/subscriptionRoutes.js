import { Router } from "express";
import {
    getPlans,
    getCurrentSubscription,
    subscribeToPlan,
    getTokenUsageStats
} from "./subscriptionController.js";

const subscriptionRouter = Router();

// Get all available plans (public route)
subscriptionRouter.get("/plans", getPlans);

// Protected routes (require authentication)
subscriptionRouter.get("/current", getCurrentSubscription);
subscriptionRouter.post("/subscribe", subscribeToPlan);
subscriptionRouter.get("/usage-stats", getTokenUsageStats);

export default subscriptionRouter;
