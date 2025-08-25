// controllers/chatController.js
import { asyncHandler, sendResponse, statusType } from "../../utils/index.js";
import Section from "../../models/section.js";
import Chat from "../../models/chat.js";
import User from "../../models/user.js";
import TokenUsage from "../../models/tokenUsage.js";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { sample_summary, researchPrompt } from "../../utils/sample.js";

// Initialize the Google Generative AI with your API key
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Helper function to approximate token count (since Gemini doesn't provide exact token count)
function approximateTokenCount(text) {
    // Rough approximation: 1 token ≈ 4 characters for English text
    // This is an estimate and may not be perfectly accurate
    return Math.ceil(text.length / 4);
}

// Create a new chat section
export const createSection = asyncHandler(async (req, res) => {
    const { title } = req.body;
    const userId = req.user._id;

    const section = await Section.create({
        title: title || "New Chat",
        user: userId
    });

    return sendResponse(res, true, section, "Section created successfully", statusType.CREATED);
});

// Get all sections for a user
export const getSections = asyncHandler(async (req, res) => {
    const userId = req.user._id;

    const sections = await Section.find({ user: userId }).sort({ updatedAt: -1 }).select("-__v");

    return sendResponse(res, true, sections, "Sections retrieved successfully", statusType.OK);
});

// Get a specific section with its chats
export const getSection = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const userId = req.user._id;

    // Verify the section belongs to the user
    const section = await Section.findOne({ _id: sectionId, user: userId });
    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    const chats = await Chat.find({ section: sectionId }).sort({ createdAt: 1 }).select("-__v");

    return sendResponse(
        res,
        true,
        { section, chats },
        "Section and chats retrieved successfully",
        statusType.OK
    );
});

// Send a message to AI and get response
export const sendMessage = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const { message, processedFiles } = req.body;
    const userId = req.user._id;

    if (!message || message.trim() === "") {
        return sendResponse(res, false, null, "Message cannot be empty", statusType.BAD_REQUEST);
    }

    // Verify the section belongs to the user
    const section = await Section.findOne({ _id: sectionId, user: userId });
    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    // Get user to check token balance
    const user = await User.findById(userId);
    if (!user) {
        return sendResponse(res, false, null, "User not found", statusType.NOT_FOUND);
    }

    // Check if user has an active subscription
    if (user.subscriptionStatus !== "active") {
        return sendResponse(res, false, null, "No active subscription", statusType.FORBIDDEN);
    }

    // Get previous messages for context
    const previousChats = await Chat.find({ section: sectionId }).sort({ createdAt: 1 }).limit(10); // Limit context to last 10 messages

    // Format previous messages for the AI
    const previousContext = previousChats.map((chat) => ({
        role: chat.isUser ? "user" : "model",
        parts: [{ text: chat.message }]
    }));

    // Save user message
    const userChat = await Chat.create({
        section: sectionId,
        message: message.trim(),
        isUser: true
    });

    // Track token usage for user message
    const userMessageTokens = approximateTokenCount(message.trim());
    await TokenUsage.create({
        user: userId,
        tokens: userMessageTokens,
        message: message.trim(),
        isUserMessage: true,
        section: sectionId
    });

    // Update user's token usage
    user.tokensUsed += userMessageTokens;
    await user.save();

    // Update section's updatedAt timestamp
    await Section.findByIdAndUpdate(sectionId, { updatedAt: new Date() });

    // Get AI response with context
    const aiResponse = await getAIResponse(message, previousContext, processedFiles);

    // Save AI response
    const aiChat = await Chat.create({
        section: sectionId,
        message: aiResponse,
        isUser: false
    });

    // Track token usage for AI response
    const aiMessageTokens = approximateTokenCount(aiResponse);
    await TokenUsage.create({
        user: userId,
        tokens: aiMessageTokens,
        message: aiResponse,
        isUserMessage: false,
        section: sectionId
    });

    // Update user's token usage with AI response tokens
    user.tokensUsed += aiMessageTokens;
    await user.save();

    return sendResponse(
        res,
        true,
        {
            userMessage: userChat,
            aiMessage: aiChat,
            tokensUsed: userMessageTokens + aiMessageTokens,
            totalTokensUsed: user.tokensUsed
        },
        "Message sent and response received",
        statusType.OK
    );
});

// Delete a section and all its chats
export const deleteSection = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const userId = req.user._id;

    // Verify the section belongs to the user
    const section = await Section.findOne({ _id: sectionId, user: userId });
    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    // Delete all chats in the section
    await Chat.deleteMany({ section: sectionId });

    // Delete all token usage records for the section
    await TokenUsage.deleteMany({ section: sectionId });

    // Delete the section
    await Section.findByIdAndDelete(sectionId);

    return sendResponse(res, true, null, "Section and chats deleted successfully", statusType.OK);
});

// Update section title
export const updateSectionTitle = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const { title } = req.body;
    const userId = req.user._id;

    if (!title || title.trim() === "") {
        return sendResponse(res, false, null, "Title cannot be empty", statusType.BAD_REQUEST);
    }

    // Verify the section belongs to the user
    const section = await Section.findOneAndUpdate(
        { _id: sectionId, user: userId },
        { title: title.trim() },
        { new: true }
    );

    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    return sendResponse(res, true, section, "Section title updated successfully", statusType.OK);
});

async function getAIResponse(message, previousContext = [], processedFiles) {
    try {
        // Try with the pro model first
        const prompt = researchPrompt
            .replace("{context_data}", JSON.stringify(processedFiles))
            .replace("{user_query}", message);

        let model;
        try {
            model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        } catch (error) {
            // If pro model fails, try with flash model
            model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        }

        // Prepare the conversation history with context
        const conversationHistory = [
            ...previousContext,
            { role: "user", parts: [{ text: prompt }] }
        ];

        // Start a chat session if we have history, otherwise start a new conversation
        const chat = model.startChat({
            history: conversationHistory,
            generationConfig: {
                maxOutputTokens: 1000,
                temperature: 0.7
            }
        });

        // Send the message and get response
        const result = await chat.sendMessage(message);
        const response = await result.response;
        const text = response.text();

        return text;
    } catch (error) {
        console.error("Error getting AI response from Gemini:", error);

        // Fallback to direct API call if SDK fails
        try {
            return await getAIResponseDirectAPI(message, previousContext);
        } catch (apiError) {
            console.error("Direct API call also failed:", apiError);
            return "I'm sorry, I'm having trouble connecting to the AI service at the moment. Please try again later.";
        }
    }
}

// Fallback function using direct API call
async function getAIResponseDirectAPI(message, previousContext = []) {
    try {
        const apiKey = process.env.GEMINI_API_KEY;
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

        // Format the contents for the API request
        const contents = [
            ...previousContext.map((item) => ({
                role: item.role.toUpperCase(), // API expects "USER" or "MODEL"
                parts: item.parts
            })),
            {
                role: "USER",
                parts: [{ text: message }]
            }
        ];

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ contents })
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    } catch (error) {
        console.error("Direct API call failed:", error);
        throw error;
    }
}
