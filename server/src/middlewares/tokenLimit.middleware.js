import { checkTokenLimit } from "../controllers/subscription/subscriptionController.js";
import { sendResponse } from "../utils/apiResonse.js";

// Function to estimate tokens from request
const estimateRequestTokens = (req) => {
    let tokenCount = 0;
    
    // Estimate tokens from message body
    if (req.body.message) {
        tokenCount += Math.ceil(req.body.message.length / 4);
    }
    
    // Estimate tokens from prompt
    if (req.body.prompt) {
        tokenCount += Math.ceil(req.body.prompt.length / 4);
    }
    
    // Add base tokens for system prompts and processing
    tokenCount += 500;
    
    // Estimate response tokens (usually 2-3x input)
    return Math.ceil(tokenCount * 2.5);
};

export const checkTokenLimitMiddleware = (estimatedTokenMultiplier = 1) => {
    return async (req, res, next) => {
        try {
            const userId = req.user._id;
            const estimatedTokens = estimateRequestTokens(req) * estimatedTokenMultiplier;
            
            const tokenCheck = await checkTokenLimit(userId, estimatedTokens);
            
            if (!tokenCheck.canProceed) {
                return res.status(429).json(
                    new sendResponse(429, {
                        reason: tokenCheck.reason,
                        tokensRemaining: tokenCheck.tokensRemaining,
                        requiredTokens: tokenCheck.requiredTokens,
                        planName: tokenCheck.planName,
                        upgradeRequired: tokenCheck.reason === "Token limit exceeded"
                    }, "Token limit exceeded. Please upgrade your plan to continue.")
                );
            }
            
            // Add token info to request for use in controllers
            req.tokenInfo = {
                estimatedTokens,
                tokensRemaining: tokenCheck.tokensRemaining
            };
            
            next();
        } catch (error) {
            console.error("Error in token limit middleware:", error);
            return res.status(500).json(
                new sendResponse(500, null, "Internal server error")
            );
        }
    };
};

// Lightweight token check for simple operations
export const lightTokenCheck = async (req, res, next) => {
    try {
        const userId = req.user._id;
        const minTokens = 100; // Minimum tokens for basic operations
        
        const tokenCheck = await checkTokenLimit(userId, minTokens);
        
        if (!tokenCheck.canProceed && tokenCheck.reason === "Token limit exceeded") {
            return res.status(429).json(
                new sendResponse(429, {
                    reason: tokenCheck.reason,
                    tokensRemaining: tokenCheck.tokensRemaining,
                    planName: tokenCheck.planName,
                    upgradeRequired: true
                }, "Token limit exceeded. Please upgrade your plan to continue.")
            );
        }
        
        req.tokenInfo = {
            tokensRemaining: tokenCheck.tokensRemaining
        };
        
        next();
    } catch (error) {
        console.error("Error in light token check:", error);
        return res.status(500).json(
            new sendResponse(500, null, "Internal server error")
        );
    }
};
