// models/chat.js
import mongoose from "mongoose";

const chatSchema = new mongoose.Schema(
    {
        section: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Section",
            required: true
        },
        message: {
            type: String,
            required: true,
            trim: true
        },
        isUser: {
            type: Boolean,
            required: true,
            default: true
        },
        model: {
            type: String,
            default: "default-ai-model"
        }
    },
    { timestamps: true }
);

export default mongoose.model("Chat", chatSchema);

// models/chat.js
// import mongoose from "mongoose";

// const chatSchema = new mongoose.Schema(
//     {
//         section: {
//             type: mongoose.Schema.Types.ObjectId,
//             ref: "Section",
//             required: true
//         },
//         message: {
//             type: String,
//             required: true,
//             trim: true
//         },
//         isUser: {
//             type: Boolean,
//             required: true,
//             default: true
//         },
//         // You can store AI model information if using multiple models
//         model: {
//             type: String,
//             default: "default-ai-model"
//         },
//         // NEW: References field for document citations
//         references: [{
//             refId: {
//                 type: String,
//                 required: false
//             },
//             fileName: {
//                 type: String,
//                 required: false
//             },
//             pageNumber: {
//                 type: Number,
//                 required: false
//             },
//             content: {
//                 type: String,
//                 required: false
//             },
//             startIndex: {
//                 type: Number,
//                 required: false
//             },
//             endIndex: {
//                 type: Number,
//                 required: false
//             },
//             documentId: {
//                 type: mongoose.Schema.Types.ObjectId,
//                 ref: "Document",
//                 required: false
//             }
//         }]
//     },
//     { timestamps: true }
// );

// // Index for better performance
// chatSchema.index({ section: 1, createdAt: 1 });
// chatSchema.index({ section: 1, isUser: 1 });

// export default mongoose.model("Chat", chatSchema);
