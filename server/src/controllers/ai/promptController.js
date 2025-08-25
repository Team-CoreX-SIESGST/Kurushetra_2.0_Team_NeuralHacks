import { GoogleGenerativeAI } from "@google/generative-ai";
import { asyncHandler } from "../../utils/asyncHandler.js";
import { ApiResponse } from "../../utils/apiResonse.js";
import { checkTokenLimit, trackTokenUsage } from "../subscription/subscriptionController.js";

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// Function to estimate tokens (rough estimation)
const estimateTokens = (text) => {
    // Rough estimation: 1 token ≈ 4 characters for English text
    return Math.ceil(text.length / 4);
};

export const improvePrompt = asyncHandler(async (req, res) => {
    const { prompt } = req.body;
    const userId = req.user._id;

    if (!prompt || prompt.trim().length === 0) {
        return res.status(400).json(
            new ApiResponse(400, null, "Prompt is required")
        );
    }

    // Estimate tokens for the request
    const estimatedInputTokens = estimateTokens(prompt);
    const estimatedOutputTokens = estimateTokens(prompt) * 1.5; // Improved prompt might be longer
    const totalEstimatedTokens = estimatedInputTokens + estimatedOutputTokens;

    // Check token limit
    const tokenCheck = await checkTokenLimit(userId, totalEstimatedTokens);
    if (!tokenCheck.canProceed) {
        return res.status(429).json(
            new ApiResponse(429, {
                reason: tokenCheck.reason,
                tokensRemaining: tokenCheck.tokensRemaining,
                requiredTokens: tokenCheck.requiredTokens,
                planName: tokenCheck.planName
            }, "Token limit exceeded")
        );
    }

    try {
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        const systemPrompt = `You are an AI prompt improvement assistant. Your job is to take user prompts and make them clearer, more specific, and more effective for getting better responses from AI systems.

When improving prompts, you should:
1. Make them more specific and detailed
2. Add context where it might be helpful
3. Structure them better for clarity
4. Remove ambiguity
5. Ensure they are actionable
6. Keep the original intent intact

Guidelines:
- If the prompt is already well-structured, make minimal improvements
- If the prompt is vague, ask for specific details or provide structure
- If the prompt is too broad, help narrow it down
- If the prompt lacks context, suggest what context might be helpful
- Keep the improved prompt concise but comprehensive
- Maintain the user's tone and style preference

Return ONLY the improved prompt, nothing else. Do not add explanations or additional text.

Original prompt: "${prompt}"

Improved prompt:`;

        const result = await model.generateContent(systemPrompt);
        const improvedPrompt = result.response.text().trim();

        // Calculate actual tokens used (approximation)
        const actualInputTokens = estimateTokens(systemPrompt);
        const actualOutputTokens = estimateTokens(improvedPrompt);
        const actualTotalTokens = actualInputTokens + actualOutputTokens;

        // Track token usage
        await trackTokenUsage(userId, actualTotalTokens, prompt, true);

        return res.status(200).json(
            new ApiResponse(200, {
                originalPrompt: prompt,
                improvedPrompt: improvedPrompt,
                tokensUsed: actualTotalTokens
            }, "Prompt improved successfully")
        );

    } catch (error) {
        console.error("Error improving prompt:", error);
        
        // Track a minimal token usage for failed requests
        await trackTokenUsage(userId, estimatedInputTokens, prompt, true);
        
        return res.status(500).json(
            new ApiResponse(500, null, "Failed to improve prompt. Please try again.")
        );
    }
});

export const suggestPromptStructure = asyncHandler(async (req, res) => {
    const { topic, purpose } = req.body;
    const userId = req.user._id;

    if (!topic) {
        return res.status(400).json(
            new ApiResponse(400, null, "Topic is required")
        );
    }

    const inputText = `${topic} ${purpose || ''}`;
    const estimatedTokens = estimateTokens(inputText) * 3; // More complex response

    // Check token limit
    const tokenCheck = await checkTokenLimit(userId, estimatedTokens);
    if (!tokenCheck.canProceed) {
        return res.status(429).json(
            new ApiResponse(429, {
                reason: tokenCheck.reason,
                tokensRemaining: tokenCheck.tokensRemaining,
                requiredTokens: tokenCheck.requiredTokens,
                planName: tokenCheck.planName
            }, "Token limit exceeded")
        );
    }

    try {
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        const systemPrompt = `Create a well-structured prompt template for the topic "${topic}"${purpose ? ` with the purpose of ${purpose}` : ''}. 

Provide a template that includes:
1. Clear context setting
2. Specific instructions
3. Desired output format
4. Any relevant constraints or guidelines

Make it professional and effective for getting good AI responses.

Return only the prompt template, nothing else.`;

        const result = await model.generateContent(systemPrompt);
        const promptTemplate = result.response.text().trim();

        // Calculate and track tokens
        const actualTokens = estimateTokens(systemPrompt) + estimateTokens(promptTemplate);
        await trackTokenUsage(userId, actualTokens, inputText, true);

        return res.status(200).json(
            new ApiResponse(200, {
                topic,
                purpose,
                promptTemplate,
                tokensUsed: actualTokens
            }, "Prompt structure suggested successfully")
        );

    } catch (error) {
        console.error("Error suggesting prompt structure:", error);
        
        const fallbackTokens = estimateTokens(inputText);
        await trackTokenUsage(userId, fallbackTokens, inputText, true);
        
        return res.status(500).json(
            new ApiResponse(500, null, "Failed to suggest prompt structure. Please try again.")
        );
    }
});
