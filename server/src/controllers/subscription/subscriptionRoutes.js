// routes/subscription.js
import express from "express";
import {
    getPlans,
    getCurrentSubscription,
    subscribeToPlan,
    getTokenUsageStats,
    createSubscriptionOrder,
    verifySubscriptionPayment
} from "./subscriptionController.js";
// import { authenticate } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get("/plans", getPlans);
router.get("/current", getCurrentSubscription);
router.post("/subscribe", subscribeToPlan);
router.get("/token-usage", getTokenUsageStats);
router.post("/create-order", createSubscriptionOrder);
router.post("/verify-payment", verifySubscriptionPayment);

export default router;
