// controllers/subscriptionController.js
import Plan from "../../models/plan.js";
import User from "../../models/user.js";
import Subscription from "../../models/subscription.js";
import TokenUsage from "../../models/tokenUsage.js";
import { asyncHandler } from "../../utils/asyncHandler.js";
import { sendResponse, statusType } from "../../utils/index.js";
import mongoose from "mongoose";
import crypto from "crypto";
import Razorpay from "razorpay";

// Initialize Razorpay instance
const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID,
    key_secret: process.env.RAZORPAY_KEY_SECRET
});

// Get all available plans
export const getPlans = asyncHandler(async (req, res) => {
    const plans = await Plan.find({ isActive: true }).sort({ price: 1 });
    return sendResponse(res, true, plans, "Plans fetched successfully", statusType.OK);
});

// Create Razorpay Order for subscription
export const createSubscriptionOrder = asyncHandler(async (req, res) => {
    const { planId } = req.body;
    const userId = req.user._id;
    console.log("Creating subscription order for user:", userId, "and plan:", planId);
    if (!planId) {
        return sendResponse(res, false, null, "Plan ID is required", statusType.BAD_REQUEST);
    }

    const plan = await Plan.findById(planId);
    if (!plan) {
        return sendResponse(res, false, null, "Plan not found", statusType.NOT_FOUND);
    }

    // For free plan, subscribe directly
    if (plan.price === 0) {
        return subscribeToPlan(req, res);
    }

    const receipt = `sub_${Date.now()}_${userId.toString().slice(-8)}`;

    const options = {
        amount: plan.price * 100,
        currency: "INR",
        receipt: receipt, // Use the shorter receipt ID
        payment_capture: 1
    };

    try {
        const razorpayOrder = await razorpay.orders.create(options);

        // Save razorpay order ID to user for verification later
        // Store the receipt instead of the order ID for verification
        await User.findByIdAndUpdate(userId, {
            razorpayReceipt: receipt, // Store the receipt instead
            pendingPlan: planId
        });

        return sendResponse(
            res,
            true,
            {
                id: razorpayOrder.id,
                currency: razorpayOrder.currency,
                amount: razorpayOrder.amount,
                planId: plan._id
            },
            "Razorpay order created successfully",
            statusType.OK
        );
    } catch (error) {
        console.error("Razorpay order error:", error);
        return sendResponse(
            res,
            false,
            null,
            "Failed to create Razorpay order",
            statusType.INTERNAL_SERVER_ERROR
        );
    }
});

// Verify subscription payment
export const verifySubscriptionPayment = asyncHandler(async (req, res) => {
    const { razorpay_payment_id, razorpay_order_id, razorpay_signature } = req.body;
    const userId = req.user._id;

    if (!razorpay_payment_id || !razorpay_order_id || !razorpay_signature) {
        return sendResponse(
            res,
            false,
            null,
            "Payment verification failed - missing parameters",
            statusType.BAD_REQUEST
        );
    }

    // Verify payment signature
    const generatedSignature = crypto
        .createHmac("sha256", process.env.RAZORPAY_KEY_SECRET)
        .update(`${razorpay_order_id}|${razorpay_payment_id}`)
        .digest("hex");

    if (generatedSignature !== razorpay_signature) {
        return sendResponse(
            res,
            false,
            null,
            "Payment verification failed - invalid signature",
            statusType.BAD_REQUEST
        );
    }

    // Get user with pending plan
    const user = await User.findById(userId);
    if (!user) {
        return sendResponse(res, false, null, "User not found", statusType.NOT_FOUND);
    }

    const planId = user.pendingPlan;
    if (!planId) {
        return sendResponse(
            res,
            false,
            null,
            "No pending subscription found",
            statusType.BAD_REQUEST
        );
    }

    const plan = await Plan.findById(planId);
    if (!plan) {
        return sendResponse(res, false, null, "Plan not found", statusType.NOT_FOUND);
    }

    // Create subscription record
    const subscription = await Subscription.create({
        user: userId,
        plan: planId,
        status: "active",
        startDate: new Date(),
        endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
        paymentId: razorpay_payment_id,
        amount: plan.price
    });

    // Update user with new plan
    await User.findByIdAndUpdate(userId, {
        plan: planId,
        tokensUsed: 0,
        tokenResetDate: new Date(),
        subscriptionStatus: "active",
        subscriptionId: subscription._id,
        razorpayOrderId: null,
        pendingPlan: null
    });

    return sendResponse(
        res,
        true,
        { plan, subscription },
        "Payment verified and subscription activated successfully",
        statusType.OK
    );
});

// Get user's current subscription details
export const getCurrentSubscription = asyncHandler(async (req, res) => {
    const userId = req.user._id;

    const user = await User.findById(userId)
        .populate("plan", "name price tokenLimit features popular")
        .select("plan tokensUsed tokenResetDate subscriptionStatus");

    if (!user) {
        return sendResponse(res, false, null, "User not found", statusType.NOT_FOUND);
    }

    // Check if token reset is due (monthly reset)
    const now = new Date();
    const resetDate = new Date(user.tokenResetDate);
    resetDate.setMonth(resetDate.getMonth() + 1);

    if (now >= resetDate) {
        await User.findByIdAndUpdate(userId, {
            tokensUsed: 0,
            tokenResetDate: now
        });
        user.tokensUsed = 0;
        user.tokenResetDate = now;
    }

    const subscriptionData = {
        plan: user.plan,
        tokensUsed: user.tokensUsed,
        tokenResetDate: user.tokenResetDate,
        subscriptionStatus: user.subscriptionStatus,
        tokensRemaining:
            user.plan.tokenLimit === -1 ? -1 : Math.max(0, user.plan.tokenLimit - user.tokensUsed)
    };

    return sendResponse(
        res,
        true,
        subscriptionData,
        "Subscription details fetched successfully",
        statusType.OK
    );
});

// Subscribe to a plan (for free plans)
export const subscribeToPlan = asyncHandler(async (req, res) => {
    const { planId } = req.body;
    const userId = req.user._id;

    if (!planId) {
        return sendResponse(res, false, null, "Plan ID is required", statusType.BAD_REQUEST);
    }

    const plan = await Plan.findById(planId);
    if (!plan) {
        return sendResponse(res, false, null, "Plan not found", statusType.NOT_FOUND);
    }

    // For free plan
    if (plan.price === 0) {
        await User.findByIdAndUpdate(userId, {
            plan: planId,
            tokensUsed: 0,
            tokenResetDate: new Date(),
            subscriptionStatus: "active"
        });

        return sendResponse(
            res,
            true,
            { plan },
            "Successfully subscribed to free plan",
            statusType.OK
        );
    }

    // For paid plans, use the Razorpay flow
    return sendResponse(
        res,
        false,
        null,
        "Paid plans require payment processing",
        statusType.BAD_REQUEST
    );
});

// Get user's token usage statistics
export const getTokenUsageStats = asyncHandler(async (req, res) => {
    const userId = req.user._id;
    const { period = "30" } = req.query;

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - parseInt(period));

    const tokenUsageStats = await TokenUsage.aggregate([
        {
            $match: {
                user: new mongoose.Types.ObjectId(userId),
                createdAt: { $gte: startDate }
            }
        },
        {
            $group: {
                _id: {
                    $dateToString: {
                        format: "%Y-%m-%d",
                        date: "$createdAt"
                    }
                },
                totalTokens: { $sum: "$tokens" },
                messageCount: { $sum: 1 }
            }
        },
        {
            $sort: { _id: 1 }
        }
    ]);

    const totalTokensUsed = await TokenUsage.aggregate([
        {
            $match: {
                user: new mongoose.Types.ObjectId(userId),
                createdAt: { $gte: startDate }
            }
        },
        {
            $group: {
                _id: null,
                totalTokens: { $sum: "$tokens" }
            }
        }
    ]);

    return sendResponse(
        res,
        true,
        {
            dailyUsage: tokenUsageStats,
            totalTokensInPeriod: totalTokensUsed[0]?.totalTokens || 0,
            period: parseInt(period)
        },
        "Token usage statistics fetched successfully",
        statusType.OK
    );
});

// Track token usage for a request
export const trackTokenUsage = async (
    userId,
    tokens,
    message,
    isUserMessage = true,
    sectionId = null
) => {
    try {
        // Create token usage record
        await TokenUsage.create({
            user: userId,
            tokens,
            message,
            isUserMessage,
            section: sectionId
        });

        // Update user's total token usage
        await User.findByIdAndUpdate(userId, {
            $inc: { tokensUsed: tokens }
        });

        return true;
    } catch (error) {
        console.error("Error tracking token usage:", error);
        return false;
    }
};

// Check if user has enough tokens for a request
export const checkTokenLimit = async (userId, requiredTokens) => {
    try {
        const user = await User.findById(userId).populate("plan");
        if (!user) {
            return { canProceed: false, reason: "User not found" };
        }

        // Check if token reset is due
        const now = new Date();
        const resetDate = new Date(user.tokenResetDate);
        resetDate.setMonth(resetDate.getMonth() + 1);

        if (now >= resetDate) {
            await User.findByIdAndUpdate(userId, {
                tokensUsed: 0,
                tokenResetDate: now
            });
            user.tokensUsed = 0;
        }

        // Unlimited tokens for Enterprise plan
        if (user.plan.tokenLimit === -1) {
            return { canProceed: true, tokensRemaining: -1 };
        }

        const tokensRemaining = user.plan.tokenLimit - user.tokensUsed;

        if (tokensRemaining < requiredTokens) {
            return {
                canProceed: false,
                reason: "Token limit exceeded",
                tokensRemaining,
                requiredTokens,
                planName: user.plan.name
            };
        }

        return {
            canProceed: true,
            tokensRemaining: tokensRemaining - requiredTokens
        };
    } catch (error) {
        console.error("Error checking token limit:", error);
        return { canProceed: false, reason: "Internal server error" };
    }
};
