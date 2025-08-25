// // controllers/chatController.js
// import { asyncHandler, sendResponse, statusType } from "../../utils/index.js";
// import Section from "../../models/section.js";
// import Chat from "../../models/chat.js";
// import { GoogleGenerativeAI } from "@google/generative-ai";

// // Initialize the Google Generative AI with your API key
// const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// // Create a new chat section
// export const createSection = asyncHandler(async (req, res) => {
//     const { title } = req.body;
//     const userId = req.user._id;

//     const section = await Section.create({
//         title: title || "New Chat",
//         user: userId
//     });

//     return sendResponse(res, true, section, "Section created successfully", statusType.CREATED);
// });

// // Get all sections for a user
// export const getSections = asyncHandler(async (req, res) => {
//     const userId = req.user._id;

//     const sections = await Section.find({ user: userId }).sort({ updatedAt: -1 }).select("-__v");

//     return sendResponse(res, true, sections, "Sections retrieved successfully", statusType.OK);
// });

// // Get a specific section with its chats
// export const getSection = asyncHandler(async (req, res) => {
//     const { sectionId } = req.params;
//     const userId = req.user._id;

//     // Verify the section belongs to the user
//     const section = await Section.findOne({ _id: sectionId, user: userId });
//     if (!section) {
//         return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
//     }

//     const chats = await Chat.find({ section: sectionId }).sort({ createdAt: 1 }).select("-__v");

//     return sendResponse(
//         res,
//         true,
//         { section, chats },
//         "Section and chats retrieved successfully",
//         statusType.OK
//     );
// });

// // Send a message to AI and get response
// export const sendMessage = asyncHandler(async (req, res) => {
//     const { sectionId } = req.params;
//     const { message } = req.body;
//     const userId = req.user._id;

//     if (!message || message.trim() === "") {
//         return sendResponse(res, false, null, "Message cannot be empty", statusType.BAD_REQUEST);
//     }

//     // Verify the section belongs to the user
//     const section = await Section.findOne({ _id: sectionId, user: userId });
//     if (!section) {
//         return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
//     }

//     // Get previous messages for context
//     const previousChats = await Chat.find({ section: sectionId }).sort({ createdAt: 1 }).limit(10); // Limit context to last 10 messages

//     // Format previous messages for the AI
//     const previousContext = previousChats.map((chat) => ({
//         role: chat.isUser ? "user" : "model",
//         parts: [{ text: chat.message }]
//     }));

//     // Save user message
//     const userChat = await Chat.create({
//         section: sectionId,
//         message: message.trim(),
//         isUser: true
//     });

//     // Update section's updatedAt timestamp
//     await Section.findByIdAndUpdate(sectionId, { updatedAt: new Date() });

//     // Get AI response with context
//     const aiResponse = await getAIResponse(message, previousContext);

//     // Save AI response
//     const aiChat = await Chat.create({
//         section: sectionId,
//         message: aiResponse,
//         isUser: false
//     });

//     return sendResponse(
//         res,
//         true,
//         {
//             userMessage: userChat,
//             aiMessage: aiChat
//         },
//         "Message sent and response received",
//         statusType.OK
//     );
// });

// // Delete a section and all its chats
// export const deleteSection = asyncHandler(async (req, res) => {
//     const { sectionId } = req.params;
//     const userId = req.user._id;

//     // Verify the section belongs to the user
//     const section = await Section.findOne({ _id: sectionId, user: userId });
//     if (!section) {
//         return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
//     }

//     // Delete all chats in the section
//     await Chat.deleteMany({ section: sectionId });

//     // Delete the section
//     await Section.findByIdAndDelete(sectionId);

//     return sendResponse(res, true, null, "Section and chats deleted successfully", statusType.OK);
// });

// // Update section title
// export const updateSectionTitle = asyncHandler(async (req, res) => {
//     const { sectionId } = req.params;
//     const { title } = req.body;
//     const userId = req.user._id;

//     if (!title || title.trim() === "") {
//         return sendResponse(res, false, null, "Title cannot be empty", statusType.BAD_REQUEST);
//     }

//     // Verify the section belongs to the user
//     const section = await Section.findOneAndUpdate(
//         { _id: sectionId, user: userId },
//         { title: title.trim() },
//         { new: true }
//     );

//     if (!section) {
//         return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
//     }

//     return sendResponse(res, true, section, "Section title updated successfully", statusType.OK);
// });

// async function getAIResponse(message, previousContext = []) {
//     try {
//         // Try with the pro model first
//         let model;
//         try {
//             model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
//         } catch (error) {
//             // If pro model fails, try with flash model
//             model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
//         }

//         // Prepare the conversation history with context
//         const conversationHistory = [
//             ...previousContext,
//             { role: "user", parts: [{ text: message }] }
//         ];

//         // Start a chat session if we have history, otherwise start a new conversation
//         const chat = model.startChat({
//             history: conversationHistory,
//             generationConfig: {
//                 maxOutputTokens: 1000,
//                 temperature: 0.7
//             }
//         });

//         // Send the message and get response
//         const result = await chat.sendMessage(message);
//         const response = await result.response;
//         const text = response.text();

//         return text;
//     } catch (error) {
//         console.error("Error getting AI response from Gemini:", error);

//         // Fallback to direct API call if SDK fails
//         try {
//             return await getAIResponseDirectAPI(message, previousContext);
//         } catch (apiError) {
//             console.error("Direct API call also failed:", apiError);
//             return "I'm sorry, I'm having trouble connecting to the AI service at the moment. Please try again later.";
//         }
//     }
// }

// // Fallback function using direct API call
// async function getAIResponseDirectAPI(message, previousContext = []) {
//     try {
//         const apiKey = process.env.GEMINI_API_KEY;
//         const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

//         // Format the contents for the API request
//         const contents = [
//             ...previousContext.map((item) => ({
//                 role: item.role.toUpperCase(), // API expects "USER" or "MODEL"
//                 parts: item.parts
//             })),
//             {
//                 role: "USER",
//                 parts: [{ text: message }]
//             }
//         ];

//         const response = await fetch(url, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify({ contents })
//         });

//         if (!response.ok) {
//             throw new Error(`API request failed with status ${response.status}`);
//         }

//         const data = await response.json();
//         return data.candidates[0].content.parts[0].text;
//     } catch (error) {
//         console.error("Direct API call failed:", error);
//         throw error;
//     }
// }

// controllers/chatController.js
import { asyncHandler, sendResponse, statusType } from "../../utils/index.js";
import Section from "../../models/section.js";
import Chat from "../../models/chat.js";
import Document from "../../models/document.js"; // NEW: Add this import
import { GoogleGenerativeAI } from "@google/generative-ai";
import document from "../../models/document.js";

import {sample_summary,researchPrompt} from "../../utils/sample.js"
// Initialize the Google Generative AI with your API key
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

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

// UPDATED: Send a message to AI and get response with document references
export const sendMessage = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const { message } = req.body;
    const userId = req.user._id;

    if (!message || message.trim() === "") {
        return sendResponse(res, false, null, "Message cannot be empty", statusType.BAD_REQUEST);
    }

    // Verify the section belongs to the user
    const section = await Section.findOne({ _id: sectionId, user: userId });
    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    // NEW: Get documents associated with this section
    const documents = await Document.find({ section: sectionId });

    // Get previous messages for context
    const previousChats = await Chat.find({ section: sectionId }).sort({ createdAt: 1 }).limit(10);

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

    // Update section's updatedAt timestamp
    await Section.findByIdAndUpdate(sectionId, { updatedAt: new Date() });

    // UPDATED: Get AI response with document context and references
    const { response: aiResponse, references } = await getAIResponseWithReferences(
        message, 
        previousContext, 
        documents
    );

    // UPDATED: Save AI response with references
    const aiChat = await Chat.create({
        section: sectionId,
        message: aiResponse,
        isUser: false,
        references: references || [] // Store reference information
    });

    return sendResponse(
        res,
        true,
        {
            userMessage: userChat,
            aiMessage: aiChat
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

    // NEW: Delete all documents in the section
    await Document.deleteMany({ section: sectionId });

    // Delete all chats in the section
    await Chat.deleteMany({ section: sectionId });

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

// NEW: Upload and process document (PDF/text)
export const uploadDocument = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const { documentContent, fileName, documentType } = req.body;
    const userId = req.user._id;

    if (!documentContent || !fileName || !documentType) {
        return sendResponse(res, false, null, "Document content, file name, and type are required", statusType.BAD_REQUEST);
    }

    // Verify section belongs to user
    const section = await Section.findOne({ _id: sectionId, user: userId });
    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    // Split document into chunks for better reference tracking
    const chunks = splitDocumentIntoChunks(documentContent, fileName);
    
    // Save document with chunks
    const document = await Document.create({
        section: sectionId,
        fileName,
        documentType,
        content: documentContent,
        chunks: chunks,
        user: userId
    });

    return sendResponse(res, true, document, "Document uploaded successfully", statusType.CREATED);
});

// NEW: Get section with documents
export const getSectionWithDocuments = asyncHandler(async (req, res) => {
    const { sectionId } = req.params;
    const userId = req.user._id;

    const section = await Section.findOne({ _id: sectionId, user: userId });
    if (!section) {
        return sendResponse(res, false, null, "Section not found", statusType.NOT_FOUND);
    }

    const chats = await Chat.find({ section: sectionId }).sort({ createdAt: 1 }).select("-__v");
    const documents = await Document.find({ section: sectionId }).select("fileName documentType createdAt");

    return sendResponse(
        res,
        true,
        { section, chats, documents },
        "Section data retrieved successfully",
        statusType.OK
    );
});

// NEW: Delete document
export const deleteDocument = asyncHandler(async (req, res) => {
    const { documentId } = req.params;
    const userId = req.user._id;

    const document = await Document.findOneAndDelete({ _id: documentId, user: userId });
    if (!document) {
        return sendResponse(res, false, null, "Document not found", statusType.NOT_FOUND);
    }

    return sendResponse(res, true, null, "Document deleted successfully", statusType.OK);
});

// UPDATED: Enhanced AI response function with document references
async function getAIResponseWithReferences(message, previousContext = [], documents = []) {
    try {
        let model;
        try {
            model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        } catch (error) {
            model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        }

        // Find relevant document chunks based on user query
        const relevantChunks = findRelevantChunks(message, documents);
        
        // Create enhanced context with document information
        const documentContext = relevantChunks.length > 0 ? 
            `\n\nDocument Context (Please reference these sections when relevant):\n${
                relevantChunks.map((chunk, index) => 
                    `[REF_${index + 1}] From "${chunk.fileName}" (Page ${chunk.pageNumber || 'N/A'}): ${chunk.content}`
                ).join('\n\n')
            }` : '';

        const enhancedMessage = message + documentContext;

        // Add system instruction for referencing
        const systemInstruction = `When answering questions, if you use information from the provided documents, please:
1. Include reference markers like [REF_1], [REF_2] etc. in your response
2. At the end of your response, list the references used
3. Be specific about which part of the document you're referencing

Example format:
"According to the document [REF_1], the process involves... 

References Used:
[REF_1] - Document: "filename.pdf", Page: 5"`;

        // Prepare conversation with system instruction
        const conversationHistory = [
            { role: "user", parts: [{ text: systemInstruction }] },
            { role: "model", parts: [{ text: "I understand. I will reference document sections when using information from them." }] },
            ...previousContext,
            { role: "user", parts: [{ text: enhancedMessage }] }
        ];

        const chat = model.startChat({
            history: conversationHistory,
            generationConfig: {
                maxOutputTokens: 1000,
                temperature: 0.7
            }
        });

        const result = await chat.sendMessage(enhancedMessage);
        const response = await result.response;
        let text = response.text();

        // Extract references from AI response
        const references = extractReferences(text, relevantChunks);

        return { response: text, references };

    } catch (error) {
        console.error("Error getting AI response:", error);

        // Fallback to original function
        try {
            const fallbackResponse = await getAIResponse(message, previousContext);
            return { response: fallbackResponse, references: [] };
        } catch (apiError) {
            console.error("Fallback also failed:", apiError);
            return { 
                response: "I'm sorry, I'm having trouble connecting to the AI service at the moment. Please try again later.",
                references: []
            };
        }
    }
}

// NEW: Function to split document into manageable chunks
function splitDocumentIntoChunks(content, fileName, chunkSize = 1000) {
    const chunks = [];
    const paragraphs = content.split('\n\n');
    let currentChunk = '';
    let chunkIndex = 0;
    let pageNumber = 1;

    for (let i = 0; i < paragraphs.length; i++) {
        const paragraph = paragraphs[i];
        
        if (currentChunk.length + paragraph.length > chunkSize && currentChunk.length > 0) {
            chunks.push({
                id: chunkIndex++,
                content: currentChunk.trim(),
                fileName,
                pageNumber,
                startIndex: chunks.length > 0 ? chunks[chunks.length - 1].endIndex : 0,
                endIndex: chunks.length > 0 ? chunks[chunks.length - 1].endIndex + currentChunk.length : currentChunk.length
            });
            currentChunk = paragraph;
            pageNumber++;
        } else {
            currentChunk += (currentChunk ? '\n\n' : '') + paragraph;
        }
    }

    if (currentChunk.trim()) {
        chunks.push({
            id: chunkIndex,
            content: currentChunk.trim(),
            fileName,
            pageNumber,
            startIndex: chunks.length > 0 ? chunks[chunks.length - 1].endIndex : 0,
            endIndex: chunks.length > 0 ? chunks[chunks.length - 1].endIndex + currentChunk.length : currentChunk.length
        });
    }

    return chunks;
}

// NEW: Function to find relevant document chunks based on query
function findRelevantChunks(query, documents, maxChunks = 3) {
    const relevantChunks = [];
    const queryLower = query.toLowerCase();
    const queryWords = queryLower.split(' ').filter(word => word.length > 2);

    documents.forEach(doc => {
        doc.chunks.forEach(chunk => {
            const chunkLower = chunk.content.toLowerCase();
            let relevanceScore = 0;

            // Simple keyword matching
            queryWords.forEach(word => {
                const wordCount = (chunkLower.match(new RegExp(word, 'g')) || []).length;
                relevanceScore += wordCount;
            });

            if (relevanceScore > 0) {
                relevantChunks.push({
                    ...chunk,
                    relevanceScore,
                    documentId: doc._id
                });
            }
        });
    });

    // Sort by relevance and return top chunks
    return relevantChunks
        .sort((a, b) => b.relevanceScore - a.relevanceScore)
        .slice(0, maxChunks);
}

// NEW: Function to extract reference information from AI response
function extractReferences(aiResponse, relevantChunks) {
    const references = [];
    const refPattern = /\[REF_(\d+)\]/g;
    let match;

    while ((match = refPattern.exec(aiResponse)) !== null) {
        const refIndex = parseInt(match[1]) - 1;
        if (refIndex >= 0 && refIndex < relevantChunks.length) {
            const chunk = relevantChunks[refIndex];
            references.push({
                refId: match[1],
                fileName: chunk.fileName,
                pageNumber: chunk.pageNumber,
                content: chunk.content.substring(0, 200) + '...', // Preview
                startIndex: chunk.startIndex,
                endIndex: chunk.endIndex,
                documentId: chunk.documentId
            });
        }
    }

    return references;
}

// Keep original function for fallback
async function getAIResponse(message, previousContext = []) {
    try {
        // Try with the pro model first
        const prompt = researchPrompt
            .replace("{context_data}", sample_summary)
            .replace("{user_query}", message);
        // console.log(prompt)
        let model;
        try {
            model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        } catch (error) {
            model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        }

        const conversationHistory = [
            ...previousContext,
            { role: "user", parts: [{ text: prompt }] }
        ];

        const chat = model.startChat({
            history: conversationHistory,
            generationConfig: {
                maxOutputTokens: 1000,
                temperature: 0.7
            }
        });

        const result = await chat.sendMessage(message);
        const response = await result.response;
        const text = response.text();

        return text;
    } catch (error) {
        console.error("Error getting AI response from Gemini:", error);

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

        const contents = [
            ...previousContext.map((item) => ({
                role: item.role.toUpperCase(),
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