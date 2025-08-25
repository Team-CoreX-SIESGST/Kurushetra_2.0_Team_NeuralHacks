import { checkTokenLimit } from "../controllers/subscriptionController.js";
import { sendResponse, statusType } from "../utils/index.js";

// Function to estimate tokens from request
const estimateRequestTokens = (req) => {
    let tokenCount = 0;

    if (req.body.message) {
        tokenCount += Math.ceil(req.body.message.length / 4);
    }

    if (req.body.prompt) {
        tokenCount += Math.ceil(req.body.prompt.length / 4);
    }

    tokenCount += 500;

    return Math.ceil(tokenCount * 2.5);
};

export const checkTokenLimitMiddleware = (estimatedTokenMultiplier = 1) => {
    return async (req, res, next) => {
        try {
            const userId = req.user._id;
            const estimatedTokens = estimateRequestTokens(req) * estimatedTokenMultiplier;

            const tokenCheck = await checkTokenLimit(userId, estimatedTokens);

            if (!tokenCheck.canProceed) {
                return sendResponse(
                    res,
                    false,
                    {
                        reason: tokenCheck.reason,
                        tokensRemaining: tokenCheck.tokensRemaining,
                        requiredTokens: tokenCheck.requiredTokens,
                        planName: tokenCheck.planName,
                        upgradeRequired: tokenCheck.reason === "Token limit exceeded"
                    },
                    "Token limit exceeded. Please upgrade your plan to continue.",
                    statusType.TOO_MANY_REQUESTS
                );
            }

            req.tokenInfo = {
                estimatedTokens,
                tokensRemaining: tokenCheck.tokensRemaining
            };

            next();
        } catch (error) {
            console.error("Error in token limit middleware:", error);
            return sendResponse(
                res,
                false,
                null,
                "Internal server error",
                statusType.INTERNAL_SERVER_ERROR
            );
        }
    };
};

export const lightTokenCheck = async (req, res, next) => {
    try {
        const userId = req.user._id;
        const minTokens = 100;

        const tokenCheck = await checkTokenLimit(userId, minTokens);

        if (!tokenCheck.canProceed && tokenCheck.reason === "Token limit exceeded") {
            return sendResponse(
                res,
                false,
                {
                    reason: tokenCheck.reason,
                    tokensRemaining: tokenCheck.tokensRemaining,
                    planName: tokenCheck.planName,
                    upgradeRequired: true
                },
                "Token limit exceeded. Please upgrade your plan to continue.",
                statusType.TOO_MANY_REQUESTS
            );
        }

        req.tokenInfo = {
            tokensRemaining: tokenCheck.tokensRemaining
        };

        next();
    } catch (error) {
        console.error("Error in light token check:", error);
        return sendResponse(
            res,
            false,
            null,
            "Internal server error",
            statusType.INTERNAL_SERVER_ERROR
        );
    }
};
