// models/document.js
import mongoose from "mongoose";

const documentSchema = new mongoose.Schema({
    section: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Section",
        required: true
    },
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
        required: true
    },
    fileName: {
        type: String,
        required: true
    },
    documentType: {
        type: String,
        enum: ['pdf', 'txt', 'docx'],
        required: true
    },
    content: {
        type: String,
        required: true
    },
    chunks: [{
        id: Number,
        content: String,
        fileName: String,
        pageNumber: Number,
        startIndex: Number,
        endIndex: Number
    }]
}, {
    timestamps: true
});

export default mongoose.model("Document", documentSchema);